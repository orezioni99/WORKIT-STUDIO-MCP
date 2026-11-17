"""Shared harness for helper processes that drive an app from outside.

The server starts `python -m workit.runners.<name> <app-id>`, writes one
JSON request to stdin and reads one marked JSON line from stdout.
"""
from __future__ import annotations

import json
import sys
import traceback

from ..bridges._core.workit_core import run_script, to_jsonable

MARK = "@@WORKIT@@"


class NotAvailable(RuntimeError):
    """The app is not running, or its automation interface is missing."""


def emit(response: dict) -> None:
    line = MARK + json.dumps(response, default=repr) + "\n"
    stream = getattr(sys.__stdout__, "buffer", None)
    if stream is not None:
        stream.write(line.encode("utf-8"))
        stream.flush()
    else:  # pragma: no cover
        sys.__stdout__.write(line)
        sys.__stdout__.flush()


def main(connect, screenshot=None) -> None:
    """connect(app_id, request) -> (namespace, info, wrap)

    namespace  names the script can use
    info       dict returned by a ping
    wrap       optional wrap(fn, label) used for modify scripts (undo grouping)
    """
    app_id = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        raw = sys.stdin.buffer.read().decode("utf-8")
        request = json.loads(raw) if raw.strip() else {}
    except Exception as error:
        emit({"ok": False, "error": f"bad request: {error}"})
        return
    try:
        namespace, info, wrap = connect(app_id, request)
    except NotAvailable as error:
        emit({"ok": False, "error": str(error)})
        return
    except Exception as error:
        emit({"ok": False, "error": f"{type(error).__name__}: {error}",
              "traceback": traceback.format_exc()})
        return
    op = request.get("op", "exec")
    if op == "ping":
        emit({"ok": True, "result": to_jsonable(info)})
        return
    if op == "screenshot":
        if screenshot is None:
            emit({"ok": False, "error": "this app has no viewport capture; export an image "
                                        "with a script instead"})
            return
        try:
            screenshot(namespace, request["path"], int(request.get("width") or 1280),
                       int(request.get("height") or 800))
            emit({"ok": True, "result": {"path": request["path"]}})
        except Exception as error:
            emit({"ok": False, "error": f"{type(error).__name__}: {error}",
                  "traceback": traceback.format_exc()})
        return
    scope = {"__name__": "__workit__"}
    scope.update(namespace)
    use_wrap = wrap if request.get("mode") == "modify" else None
    emit(run_script(request.get("code") or "", scope, use_wrap, request.get("label") or "WorkitStudio"))
