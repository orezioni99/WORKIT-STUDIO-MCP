# -*- coding: utf-8 -*-
"""WorkitStudio for FreeCAD 0.21 and later (folder: <user data>/Mod/WorkitStudio)."""
import FreeCAD
import FreeCADGui
from PySide import QtCore  # FreeCAD's shim: PySide2 or PySide6 underneath

import workit_core as core

PORT = 47850
_state = {}


def _prepare(namespace):
    namespace["doc"] = FreeCAD.ActiveDocument


def _wrap(fn, label):
    doc = FreeCAD.ActiveDocument
    if doc is None:
        return fn()
    doc.openTransaction(label)
    try:
        value = fn()
    except BaseException:
        doc.abortTransaction()
        raise
    doc.commitTransaction()
    return value


def _after(mode, ok):
    doc = FreeCAD.ActiveDocument
    if doc is not None and mode == "modify":
        doc.recompute()


def _screenshot(path, width, height):
    view = FreeCADGui.ActiveDocument.ActiveView
    view.saveImage(path, width, height, "Current")


def _info():
    doc = FreeCAD.ActiveDocument
    return {"version": ".".join(FreeCAD.Version()[:3]), "file": doc.FileName if doc else None}


def start():
    if _state.get("bridge"):
        return _state["bridge"]
    bridge = core.Bridge(
        "freecad", PORT,
        namespace={"FreeCAD": FreeCAD, "App": FreeCAD, "FreeCADGui": FreeCADGui,
                   "Gui": FreeCADGui},
        prepare=_prepare, wrap=_wrap, after=_after, screenshot=_screenshot, info=_info,
        log=lambda text: FreeCAD.Console.PrintMessage(text + "\n"),
    )
    bridge.start()
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: bridge.pump())
    timer.start(50)
    _state.update(bridge=bridge, timer=timer)
    return bridge
