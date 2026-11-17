"""How the server reaches each kind of app. All calls here block; the server
runs them in worker threads."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .bridges._core import workit_core as core
from .registry import APPS, App

MARK = "@@WORKIT@@"
PING_TIMEOUT = 0.35


class BridgeError(RuntimeError):
    """The app could not be reached or the request could not be delivered."""


def home() -> Path:
    path = Path(core.home_dir())
    path.mkdir(parents=True, exist_ok=True)
    return path


def token() -> str:
    return core.read_token()


# ------------------------------------------------------------------ processes
def running_processes() -> set[str]:
    """Lower-case names of running executables (best effort, never raises)."""
    try:
        if os.name == "nt":
            out = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"], capture_output=True, timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            ).stdout.decode("mbcs", "replace")
            return {line.split('","')[0].strip('"').lower() for line in out.splitlines() if line}
        out = subprocess.run(["ps", "-A", "-o", "comm="], capture_output=True, timeout=10)
        return {os.path.basename(line.strip()).lower() for line in out.stdout.decode().splitlines()}
    except Exception:
        return set()


# -------------------------------------------------------------- socket bridge
def socket_request(port: int, payload: dict, timeout: float, connect_timeout: float = 2.0) -> dict:
    message = dict(payload, token=token(), id=uuid.uuid4().hex[:8])
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=connect_timeout)
    except OSError as error:
        raise BridgeError(f"nothing is listening on 127.0.0.1:{port} ({error})") from None
    try:
        sock.settimeout(timeout)
        sock.sendall(json.dumps(message).encode("utf-8") + b"\n")
        chunks = []
        while True:
            chunk = sock.recv(1 << 16)
            if not chunk:
                break
            chunks.append(chunk)
            if chunk.endswith(b"\n"):
                break
    except socket.timeout:
        raise BridgeError(f"no answer from the app within {int(timeout)}s") from None
    except OSError as error:
        raise BridgeError(f"connection to the app dropped ({error})") from None
    finally:
        sock.close()
    data = b"".join(chunks).strip()
    if not data:
        raise BridgeError("the app closed the connection without answering")
    try:
        return json.loads(data.decode("utf-8"))
    except ValueError:
        raise BridgeError("the app sent an answer that is not JSON") from None


def socket_instances(app: App) -> list[dict]:
    """Ping every port an app's bridge may use; return the live ones."""
    ports = [app.port + offset for offset in range(core.PORT_SPAN)]

    def ping(port: int):
        try:
            reply = socket_request(port, {"op": "ping"}, PING_TIMEOUT, PING_TIMEOUT)
        except BridgeError:
            return None
        if reply.get("ok") and reply.get("result", {}).get("app") == app.id:
            return reply["result"]
        return None

    with ThreadPoolExecutor(max_workers=len(ports)) as pool:
        return [found for found in pool.map(ping, ports) if found]


def _socket_port(app: App, instance: int | None) -> int:
    if instance:
        return int(instance)
    live = socket_instances(app)
    if not live:
        raise BridgeError(f"{app.name} is not connected. {app.setup}")
    return int(live[0]["port"])


# ----------------------------------------------------------- runner processes
def run_runner(app: App, request: dict, timeout: float) -> dict:
    """Run a helper process that connects to the app from outside."""
    command = [sys.executable, "-m", f"workit.runners.{app.runner}", app.id]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    try:
        done = subprocess.run(
            command, input=json.dumps(request).encode("utf-8"), capture_output=True,
            timeout=timeout + 15, env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired:
        raise BridgeError(
            f"the script did not finish within {int(timeout)}s and was stopped "
            f"(is {app.name} showing a dialog or busy with a command?)"
        ) from None
    out = done.stdout.decode("utf-8", "replace")
    for line in reversed(out.splitlines()):
        if line.startswith(MARK):
            return json.loads(line[len(MARK):])
    tail = (done.stderr.decode("utf-8", "replace") or out).strip()[-1500:]
    raise BridgeError(f"the {app.name} helper failed to start or crashed:\n{tail}")


# ---------------------------------------------------------------------- Revit
def revit_request(port: int, route: str, payload: dict | None, timeout: float) -> dict:
    url = f"http://127.0.0.1:{port}/workit/{route}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(dict(payload, token=token())).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers,
                                     method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as reply:
            body = reply.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        if error.code == 404:
            raise BridgeError("pyRevit Routes is running but the WorkitStudio extension is not "
                              "loaded. Run `workit install revit` and reload pyRevit.") from None
    except (urllib.error.URLError, OSError) as error:
        raise BridgeError(f"pyRevit Routes did not answer on port {port} ({error})") from None
    try:
        parsed = json.loads(body)
    except ValueError:
        raise BridgeError(f"pyRevit Routes sent an unexpected answer: {body[:300]}") from None
    if isinstance(parsed, str):  # some pyRevit versions double-encode
        try:
            parsed = json.loads(parsed)
        except ValueError:
            pass
    if not isinstance(parsed, dict):
        raise BridgeError(f"pyRevit Routes sent an unexpected answer: {body[:300]}")
    if "ok" not in parsed and "exception" in parsed:  # pyRevit's own error envelope
        detail = parsed["exception"]
        message = detail.get("message") if isinstance(detail, dict) else str(detail)
        return {"ok": False, "error": message or "pyRevit Routes reported an error",
                "traceback": detail.get("traceback", "") if isinstance(detail, dict) else ""}
    return parsed


def revit_instances(app: App) -> list[dict]:
    ports = [app.port + offset for offset in range(core.PORT_SPAN)]

    def ping(port: int):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=PING_TIMEOUT):
                pass
        except OSError:
            return None
        try:
            reply = revit_request(port, "ping", None, 5)
        except BridgeError as error:
            return {"port": port, "ready": False, "problem": str(error)}
        info = reply.get("result", reply)
        if isinstance(info, dict):
            return dict(info, port=port, ready=True)
        return {"port": port, "ready": True}

    with ThreadPoolExecutor(max_workers=len(ports)) as pool:
        return [found for found in pool.map(ping, ports) if found]


# ------------------------------------------------------------------ dispatch
def status(app: App, processes: set[str]) -> dict:
    """Is the app reachable right now?"""
    running = any(name in processes for name in app.processes)
    if app.kind == "socket":
        live = socket_instances(app)
        if live:
            return {"state": "connected", "instances": live}
        if running:
            return {"state": "running, bridge not loaded", "next": app.setup}
        return {"state": "not running"}
    if app.kind == "revit":
        live = revit_instances(app)
        ready = [item for item in live if item.get("ready")]
        if ready:
            return {"state": "connected", "instances": ready}
        if live:
            return {"state": "running, bridge not loaded", "next": live[0].get("problem", app.setup)}
        if running:
            return {"state": "running, bridge not loaded", "next": app.setup}
        return {"state": "not running"}
    if app.kind == "unreal":
        if not running:
            return {"state": "not running"}
        from . import unreal
        try:
            found = unreal.discover(wait=1.5)
        except (BridgeError, OSError):
            return {"state": "running, remote execution off", "next": app.setup}
        return {"state": "connected", "instances": [{
            "project": found.get("project_name"), "version": found.get("engine_version")}]}
    return {"state": "running" if running else "not running"}


def execute(app: App, code: str, mode: str, timeout: float, instance: int | None = None,
            label: str = "WorkitStudio") -> dict:
    """Run a script in/against an app. Returns the bridge response dict."""
    request = {"op": "exec", "code": code, "mode": mode, "timeout": timeout, "label": label}
    if app.kind == "socket":
        port = _socket_port(app, instance)
        return socket_request(port, request, timeout + 10)
    if app.kind == "revit":
        port = int(instance) if instance else None
        if port is None:
            live = [item for item in revit_instances(app) if item.get("ready")]
            if not live:
                raise BridgeError(f"Revit is not connected. {app.setup}")
            port = live[0]["port"]
        return revit_request(port, "exec", request, timeout + 10)
    if app.kind == "unreal":
        from . import unreal

        return unreal.execute(code, timeout, mode, label)
    if app.kind == "runner":
        if instance:
            request["instance"] = int(instance)
        return run_runner(app, request, timeout)
    raise BridgeError(f"no transport for {app.id}")


def screenshot(app: App, width: int, height: int, instance: int | None = None) -> bytes:
    """Capture what the app shows as PNG bytes.

    In-app bridges render their own viewport. Every other app (and any bridge
    whose capture fails) falls back to a picture of the app's main window.
    """
    problem = ""
    if app.kind == "socket":
        shots = home() / "shots"
        shots.mkdir(exist_ok=True)
        path = shots / f"{app.id}-{int(time.time() * 1000)}.png"
        request = {"op": "screenshot", "path": str(path), "width": width, "height": height,
                   "timeout": 60}
        reply = socket_request(_socket_port(app, instance), request, 70)
        if reply.get("ok") and path.exists():
            try:
                return path.read_bytes()
            finally:
                try:
                    path.unlink()
                except OSError:
                    pass
        problem = reply.get("error") or "the bridge did not write an image"
    from . import wincapture

    try:
        return wincapture.capture(app.processes, width, height)
    except wincapture.CaptureError as error:
        detail = f"{problem}; window capture: {error}" if problem else str(error)
        raise BridgeError(detail) from None


def all_status() -> list[dict]:
    processes = running_processes()
    with ThreadPoolExecutor(max_workers=12) as pool:
        states = list(pool.map(lambda app: status(app, processes), APPS))
    rows = []
    for app, state in zip(APPS, states):
        rows.append({"app": app.id, "name": app.name, "family": app.family,
                     "script_language": app.language, **state})
    return rows
