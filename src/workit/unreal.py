"""Unreal Editor through its built-in Python remote execution protocol.

Nothing is installed in Unreal. The user enables "Remote Execution" in
Project Settings > Plugins > Python. The protocol: find the editor with a UDP
multicast ping, ask it to open a TCP connection back to us, send the script.
"""
from __future__ import annotations

import json
import socket
import struct
import time
import uuid

from .adapters import BridgeError

MAGIC = "ue_py"
VERSION = 1
GROUP = ("239.0.0.1", 6766)
BIND = "127.0.0.1"
COMMAND = ("127.0.0.1", 6776)
MARK = "@@WORKIT@@"

_WRAPPER = '''\
import json as _ob_json, traceback as _ob_tb
_ob_scope = globals()
_ob_scope.pop("result", None)
_ob_reply = {"ok": True}
try:
    import unreal
    _ob_code = compile(%(code)r, "<workit>", "exec")
    if %(modify)r:
        with unreal.ScopedEditorTransaction(%(label)r):
            exec(_ob_code, _ob_scope)
    else:
        exec(_ob_code, _ob_scope)
    _ob_reply["result"] = _ob_scope.get("result")
except BaseException as _ob_error:
    _ob_reply = {"ok": False, "error": "%%s: %%s" %% (type(_ob_error).__name__, _ob_error),
                 "traceback": _ob_tb.format_exc()}
print(%(mark)r + _ob_json.dumps(_ob_reply, default=repr))
'''


def _message(kind: str, source: str, dest: str | None = None, data: dict | None = None) -> bytes:
    body = {"version": VERSION, "magic": MAGIC, "type": kind, "source": source}
    if dest:
        body["dest"] = dest
    if data:
        body["data"] = data
    return json.dumps(body).encode("utf-8")


def _udp() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((BIND, GROUP[1]))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(BIND))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 0)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                    struct.pack("=4s4s", socket.inet_aton(GROUP[0]), socket.inet_aton(BIND)))
    sock.settimeout(0.2)
    return sock


def _find_editor(udp: socket.socket, node: str, wait: float = 3.0) -> dict:
    end = time.time() + wait
    last_ping = 0.0
    while time.time() < end:
        if time.time() - last_ping > 0.5:
            udp.sendto(_message("ping", node), GROUP)
            last_ping = time.time()
        try:
            data, _ = udp.recvfrom(65536)
        except socket.timeout:
            continue
        try:
            message = json.loads(data.decode("utf-8"))
        except ValueError:
            continue
        if message.get("magic") == MAGIC and message.get("type") == "pong" \
                and message.get("dest") == node:
            return message
    raise BridgeError(
        "No Unreal Editor answered. Open a project, enable the Python Editor Script Plugin, "
        "and turn on Project Settings > Plugins > Python > Enable Remote Execution."
    )


def discover(wait: float = 3.0) -> dict:
    """Return the first editor that answers the ping (project name, engine version)."""
    node = str(uuid.uuid4())
    udp = _udp()
    try:
        return _find_editor(udp, node, wait).get("data", {})
    finally:
        udp.close()


def execute(code: str, timeout: float, mode: str = "read", label: str = "WorkitStudio") -> dict:
    node = str(uuid.uuid4())
    try:
        udp = _udp()
    except OSError as error:
        raise BridgeError(f"could not open the Unreal discovery socket ({error})") from None
    listener = None
    channel = None
    try:
        editor = _find_editor(udp, node)["source"]
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(COMMAND)
        listener.listen(1)
        listener.settimeout(0.5)
        opening = _message("open_connection", node, editor,
                           {"command_ip": COMMAND[0], "command_port": COMMAND[1]})
        end = time.time() + 6.0
        while channel is None and time.time() < end:
            udp.sendto(opening, GROUP)
            try:
                channel, _ = listener.accept()
            except socket.timeout:
                continue
        if channel is None:
            raise BridgeError("Unreal Editor answered the ping but did not connect back.")
        script = _WRAPPER % {"code": code, "modify": mode == "modify", "label": label,
                             "mark": MARK}
        channel.settimeout(timeout + 5)
        channel.sendall(_message("command", node, editor, {
            "command": script, "unattended": True, "exec_mode": "ExecuteFile"}))
        buffer = b""
        reply = None
        while reply is None:
            try:
                chunk = channel.recv(1 << 16)
            except socket.timeout:
                raise BridgeError(f"Unreal did not finish within {int(timeout)}s") from None
            if not chunk:
                break
            buffer += chunk
            try:
                reply = json.loads(buffer.decode("utf-8"))
            except ValueError:
                continue
        if reply is None:
            raise BridgeError("Unreal closed the connection without a result.")
        return _parse(reply.get("data", {}))
    finally:
        try:
            udp.sendto(_message("close_connection", node), GROUP)
        except OSError:
            pass
        for sock in (channel, listener, udp):
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass


def _parse(data: dict) -> dict:
    lines = []
    for entry in data.get("output") or []:
        text = entry.get("output", "") if isinstance(entry, dict) else str(entry)
        lines.extend(text.splitlines())
    result = None
    stdout = []
    for line in lines:
        if line.startswith(MARK):
            try:
                result = json.loads(line[len(MARK):])
            except ValueError:
                stdout.append(line)
        else:
            stdout.append(line)
    if result is None:
        return {"ok": bool(data.get("success")), "result": data.get("result"),
                "stdout": "\n".join(stdout),
                **({} if data.get("success") else {"error": "Unreal reported a failure"})}
    result["stdout"] = "\n".join(stdout)
    return result
