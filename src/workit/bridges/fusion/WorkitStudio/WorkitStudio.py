# -*- coding: utf-8 -*-
"""WorkitStudio add-in for Autodesk Fusion.

Worker threads must never touch Fusion, so the socket thread queues the script
and fires a custom event; Fusion then calls us back on its main thread.
"""
import os
import sys
import traceback

import adsk.core
import adsk.fusion

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import workit_core as core

PORT = 47870
EVENT_ID = "WorkitStudioPumpEvent"
_app = None
_bridge = None
_event = None
_handlers = []


class _PumpHandler(adsk.core.CustomEventHandler):
    def notify(self, args):
        try:
            if _bridge is not None:
                _bridge.pump()
        except Exception:
            _app.log("WorkitStudio: " + traceback.format_exc())


def _prepare(namespace):
    design = adsk.fusion.Design.cast(_app.activeProduct)
    ui = _app.userInterface
    namespace["design"] = design
    namespace["root"] = design.rootComponent if design else None
    namespace["ui"] = ui
    try:  # end any command the user left running, or edits fail
        if ui.activeCommand != "SelectCommand":
            ui.commandDefinitions.itemById("SelectCommand").execute()
    except Exception:
        pass


def _screenshot(path, width, height):
    _app.activeViewport.saveAsImageFile(path, width, height)


def run(context):
    global _app, _bridge, _event
    _app = adsk.core.Application.get()
    try:
        _app.unregisterCustomEvent(EVENT_ID)
    except Exception:
        pass
    _event = _app.registerCustomEvent(EVENT_ID)
    handler = _PumpHandler()
    _event.add(handler)
    _handlers.append(handler)
    _bridge = core.Bridge(
        "fusion", PORT, namespace={"adsk": adsk, "app": _app},
        prepare=_prepare, screenshot=_screenshot,
        info={"version": _app.version},
        wake=lambda: _app.fireCustomEvent(EVENT_ID, ""),
        log=_app.log,
    )
    _bridge.start()


def stop(context):
    global _bridge
    if _bridge is not None:
        _bridge.stop()
        _bridge = None
    try:
        _app.unregisterCustomEvent(EVENT_ID)
    except Exception:
        pass
    del _handlers[:]
