# -*- coding: utf-8 -*-
"""WorkitStudio in-app core.

This single file runs INSIDE a host application (Blender, Rhino, 3ds Max,
FreeCAD, Maya, Fusion, Cinema 4D, Houdini, QGIS ...). It has no dependencies
and works on Python 2.7 (IronPython included) up to current Python 3.

A host shim creates one ``Bridge`` and tells it how to reach the app's main
thread, either by calling ``bridge.pump()`` from a timer, or by passing a
``wake`` callable that schedules ``bridge.pump`` on the main thread.

Wire protocol (one request per TCP connection, localhost only):
    request : one line of JSON  {"token", "op", "code", "mode", "timeout", ...}
    response: one line of JSON  {"ok", "result", "stdout", "error", "traceback"}
"""
from __future__ import print_function

import json
import numbers
import os
import socket
import sys
import threading
import time
import traceback

try:
    import queue
except ImportError:  # Python 2
    import Queue as queue

try:
    text_type = unicode  # noqa: F821  (Python 2)
except NameError:
    text_type = str

PROTOCOL = 1
PORT_SPAN = 5  # a second/third instance of the same app takes the next port
MAX_REQUEST = 16 * 1024 * 1024
MAX_TEXT = 200000
_REGISTRY_ATTR = "_workit_instances"


def home_dir():
    return os.environ.get("WORKIT_HOME") or os.path.join(
        os.path.expanduser("~"), ".workit"
    )


def read_token():
    """Shared secret between the MCP server and the bridges (same user account)."""
    env = os.environ.get("WORKIT_TOKEN")
    if env:
        return env.strip()
    path = os.path.join(home_dir(), "token")
    try:
        with open(path, "r") as handle:
            token = handle.read().strip()
        if token:
            return token
    except (IOError, OSError):
        pass
    import binascii

    token = binascii.hexlify(os.urandom(24)).decode("ascii")
    try:
        if not os.path.isdir(home_dir()):
            os.makedirs(home_dir())
    except (IOError, OSError):
        pass
    try:
        # exclusive create: if another thread or process wins the race, use theirs
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        try:
            os.write(descriptor, token.encode("ascii"))
        finally:
            os.close(descriptor)
    except (IOError, OSError):
        for _attempt in range(20):
            try:
                with open(path, "r") as handle:
                    existing = handle.read().strip()
                if existing:
                    return existing
            except (IOError, OSError):
                pass
            time.sleep(0.05)
    return token


def _same(a, b):
    try:
        import hmac

        return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
    except Exception:
        return a == b


class _Capture(object):
    """Collects everything a script prints."""

    def __init__(self):
        self.parts = []

    def write(self, data):
        try:
            if not isinstance(data, text_type):
                data = data.decode("utf-8", "replace")
        except Exception:
            data = repr(data)
        self.parts.append(data)
        return len(data)

    def flush(self):
        pass

    def isatty(self):
        return False

    def getvalue(self):
        return u"".join(self.parts)


def _clip(text):
    if text and len(text) > MAX_TEXT:
        return text[:MAX_TEXT] + u"\n... [truncated %d characters]" % (len(text) - MAX_TEXT)
    return text


def to_jsonable(value, depth=0):
    """Turn any script result into something JSON can carry."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, text_type):
        return value
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except Exception:
            return repr(value)
    if isinstance(value, numbers.Integral):
        return int(value)
    if isinstance(value, numbers.Real):
        number = float(value)
        if number != number or number in (float("inf"), float("-inf")):
            return repr(number)
        return number
    if depth > 12:
        return _safe_repr(value)
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            out[key if isinstance(key, text_type) else _safe_repr(key).strip("'")] = to_jsonable(
                item, depth + 1
            )
        return out
    if isinstance(value, (list, tuple, set, frozenset)):
        return [to_jsonable(item, depth + 1) for item in value]
    return _safe_repr(value)


def _safe_repr(value):
    try:
        return repr(value)
    except Exception:
        return "<unprintable %s>" % type(value).__name__


def compile_script(code):
    """Compile a script; if it ends with an expression, return that separately
    so its value becomes the result (like a REPL)."""
    try:
        import ast

        tree = ast.parse(code, "<workit>", "exec")
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = tree.body.pop()
            body = compile(tree, "<workit>", "exec")
            tail = compile(ast.Expression(last.value), "<workit>", "eval")
            return body, tail
    except SyntaxError:
        raise
    except Exception:
        pass
    return compile(code, "<workit>", "exec"), None


def run_script(code, namespace, wrap=None, label="WorkitStudio"):
    """Execute ``code`` in ``namespace``. Returns the response dict.

    The result is the script's ``result`` variable if it sets one, otherwise
    the value of its last expression. Printed text comes back as ``stdout``.
    """
    capture = _Capture()
    old_out, old_err = sys.stdout, sys.stderr
    started = time.time()
    response = {"ok": True}
    namespace.pop("result", None)

    def body():
        main, tail = compile_script(code)
        exec(main, namespace)
        value = eval(tail, namespace) if tail is not None else None
        if "result" in namespace:
            value = namespace["result"]
        return value

    sys.stdout = sys.stderr = capture
    try:
        value = wrap(body, label) if wrap else body()
        response["result"] = to_jsonable(value)
    except BaseException as error:  # scripts may raise SystemExit; keep the app alive
        response["ok"] = False
        response["error"] = "%s: %s" % (type(error).__name__, error)
        response["traceback"] = _clip(traceback.format_exc())
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    response["stdout"] = _clip(capture.getvalue())
    response["elapsed_ms"] = int((time.time() - started) * 1000)
    return response


class _Job(object):
    def __init__(self, work):
        self.work = work
        self.done = threading.Event()
        self.cancelled = False
        self.response = None

    def run(self):
        if self.cancelled:
            return
        try:
            self.response = self.work()
        except BaseException as error:
            self.response = {
                "ok": False,
                "error": "%s: %s" % (type(error).__name__, error),
                "traceback": _clip(traceback.format_exc()),
            }
        self.done.set()


class Bridge(object):
    """Localhost listener that runs scripts on the host's main thread.

    app         short id, e.g. "blender"
    port        first port to try (the next PORT_SPAN-1 are fallbacks)
    namespace   dict of names every script can use (bpy, rs, doc ...)
    prepare     prepare(namespace) called on the main thread before each script
    wrap        wrap(fn, label) runs fn inside the host's undo step (modify only)
    after       after(mode, ok) called on the main thread after each script
    screenshot  screenshot(path, width, height) saves the viewport as PNG
    wake        wake() must make the host call bridge.pump() on its main thread
                soon. Leave None when a host timer already calls pump().
    info        dict or callable returning a dict, merged into the ping reply
    """

    def __init__(self, app, port, namespace=None, prepare=None, wrap=None, after=None,
                 screenshot=None, wake=None, info=None, log=None):
        self.app = app
        self.base_port = int(port)
        self.port = None
        self.namespace = {"__name__": "__workit__"}
        if namespace:
            self.namespace.update(namespace)
        self.prepare = prepare
        self.wrap = wrap
        self.after = after
        self.screenshot = screenshot
        self.wake = wake
        self.info = info
        self.log = log or (lambda message: None)
        self._jobs = queue.Queue()
        self._socket = None
        self._thread = None
        self._running = False
        self._busy = False

    # ---------------------------------------------------------------- lifecycle
    def start(self):
        registry = sys.__dict__.setdefault(_REGISTRY_ATTR, {})
        previous = registry.get(self.app)
        if previous is not None and previous is not self:
            try:
                previous.stop()
            except Exception:
                pass
        last_error = None
        for offset in range(PORT_SPAN):
            candidate = self.base_port + offset
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                if os.name == "nt":
                    exclusive = getattr(socket, "SO_EXCLUSIVEADDRUSE", None)
                    if exclusive is not None:
                        sock.setsockopt(socket.SOL_SOCKET, exclusive, 1)
                else:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("127.0.0.1", candidate))
                sock.listen(8)
                sock.settimeout(0.5)
            except (socket.error, OSError) as error:
                last_error = error
                try:
                    sock.close()
                except Exception:
                    pass
                continue
            self._socket = sock
            self.port = candidate
            break
        if self._socket is None:
            self.log("WorkitStudio: no free port from %d (%s)" % (self.base_port, last_error))
            return False
        self._running = True
        self._thread = threading.Thread(target=self._serve, name="workit-" + self.app)
        self._thread.daemon = True
        self._thread.start()
        registry[self.app] = self
        self.log("WorkitStudio: %s is listening on 127.0.0.1:%d" % (self.app, self.port))
        return True

    def stop(self):
        self._running = False
        sock, self._socket = self._socket, None
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass
        registry = sys.__dict__.get(_REGISTRY_ATTR, {})
        if registry.get(self.app) is self:
            del registry[self.app]

    # ------------------------------------------------------------- main thread
    def pump(self, budget=20):
        """Run queued scripts. Call this on the host's main thread."""
        count = 0
        while count < budget:
            try:
                job = self._jobs.get_nowait()
            except queue.Empty:
                break
            self._busy = True
            try:
                job.run()
            finally:
                self._busy = False
            count += 1
        return count

    # ----------------------------------------------------------- socket thread
    def _serve(self):
        while self._running:
            sock = self._socket
            if sock is None:
                break
            try:
                conn, _addr = sock.accept()
            except socket.timeout:
                continue
            except (socket.error, OSError):
                if self._running:
                    time.sleep(0.2)
                continue
            worker = threading.Thread(target=self._client, args=(conn,))
            worker.daemon = True
            worker.start()

    def _client(self, conn):
        try:
            conn.settimeout(10.0)
            data = b""
            while b"\n" not in data:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                data += chunk
                if len(data) > MAX_REQUEST:
                    return
            line = data.split(b"\n", 1)[0]
            try:
                request = json.loads(line.decode("utf-8"))
            except Exception:
                return  # not our protocol (for example a browser): hang up silently
            if not isinstance(request, dict):
                return
            if not _same(text_type(request.get("token", "")), text_type(read_token())):
                self._send(conn, {"ok": False, "error": "bad token"})
                return
            response = self._route(request)
            if "id" in request:
                response["id"] = request["id"]
            self._send(conn, response)
        except Exception:
            self.log("WorkitStudio: connection error\n" + traceback.format_exc())
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _send(self, conn, response):
        try:
            payload = json.dumps(response)
        except Exception:
            payload = json.dumps({"ok": False, "error": "response was not serialisable"})
        if not isinstance(payload, bytes):
            payload = payload.encode("utf-8")
        conn.settimeout(30.0)
        conn.sendall(payload + b"\n")

    def _route(self, request):
        op = request.get("op", "ping")
        if op == "ping":
            reply = {
                "app": self.app,
                "protocol": PROTOCOL,
                "port": self.port,
                "pid": os.getpid(),
                "python": sys.version.split()[0],
                "busy": self._busy,
                "screenshot": self.screenshot is not None,
            }
            extra = self.info
            try:
                extra = extra() if callable(extra) else extra
                if extra:
                    reply.update(to_jsonable(extra))
            except Exception:
                pass
            return {"ok": True, "result": reply}
        if op == "exec":
            code = request.get("code")
            if not isinstance(code, text_type) and not isinstance(code, str):
                return {"ok": False, "error": "missing code"}
            mode = request.get("mode", "read")
            label = request.get("label") or "WorkitStudio"
            return self._on_main(lambda: self._exec(code, mode, label), request)
        if op == "screenshot":
            if self.screenshot is None:
                return {"ok": False, "error": "this app's bridge cannot capture the viewport"}
            path = request.get("path")
            width = int(request.get("width") or 1280)
            height = int(request.get("height") or 800)

            def shoot():
                self.screenshot(path, width, height)
                return {"ok": True, "result": {"path": path}}

            return self._on_main(shoot, request)
        return {"ok": False, "error": "unknown op %r" % (op,)}

    def _exec(self, code, mode, label):
        if self.prepare:
            self.prepare(self.namespace)
        wrap = self.wrap if mode == "modify" else None
        response = run_script(code, self.namespace, wrap, label)
        if self.after:
            try:
                self.after(mode, response.get("ok", False))
            except Exception:
                pass
        return response

    def _on_main(self, work, request):
        timeout = float(request.get("timeout") or 120)
        job = _Job(work)
        self._jobs.put(job)
        if self.wake:
            try:
                self.wake()
            except Exception:
                self.log("WorkitStudio: wake failed\n" + traceback.format_exc())
        if not job.done.wait(timeout):
            job.cancelled = True
            return {
                "ok": False,
                "error": "timed out after %ss waiting for the app (is a dialog open, a "
                         "command running, or the script still working?)" % int(timeout),
            }
        return job.response
