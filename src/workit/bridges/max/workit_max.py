# -*- coding: utf-8 -*-
"""WorkitStudio for 3ds Max 2021 and later.

Loaded at startup by a one-line MAXScript stub in the user startup folder:
    python.ExecuteFile @"<this file>"
Python threads may not touch 3ds Max, so the socket thread only queues work
and a Qt timer on the main thread runs it.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pymxs

try:
    from PySide6 import QtCore  # 3ds Max 2025+
except ImportError:
    from PySide2 import QtCore  # 3ds Max 2021-2024

import workit_core as core

PORT = 47830
rt = pymxs.runtime


def mxs(code):
    """Run a MAXScript string and return its value."""
    return rt.execute(code)


def _wrap(fn, label):
    with pymxs.undo(True, label):
        return fn()


def _after(mode, ok):
    rt.redrawViews()


def _screenshot(path, width, height):
    bitmap = rt.gw.getViewportDib()
    bitmap.filename = path
    rt.save(bitmap)
    rt.close(bitmap)


def _info():
    return {"version": str(rt.maxVersion()[0]), "file": str(rt.maxFilePath) + str(rt.maxFileName)}


def start():
    bridge = core.Bridge("3dsmax", PORT, namespace={"pymxs": pymxs, "rt": rt, "mxs": mxs},
                         wrap=_wrap, after=_after, screenshot=_screenshot, info=_info,
                         log=print)
    bridge.start()
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: bridge.pump())
    timer.start(50)
    # keep both alive for the whole session
    sys.modules[__name__ if __name__ != "__main__" else "workit_max_state"] = sys.modules.get(__name__)
    start.keep = (bridge, timer)
    return bridge


start()
