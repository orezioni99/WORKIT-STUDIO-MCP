# -*- coding: utf-8 -*-
"""WorkitStudio for Houdini 20.5 and later.

Installed as a Houdini package; uiready.py (next to this file) imports this
module once the interface is up.
"""
import hdefereval
import hou

import workit_core as core

PORT = 47890
_state = {}


def _wrap(fn, label):
    with hou.undos.group(label):
        return fn()


def start():
    if _state.get("bridge"):
        return _state["bridge"]
    holder = {}
    bridge = core.Bridge(
        "houdini", PORT, namespace={"hou": hou}, wrap=_wrap,
        info={"version": hou.applicationVersionString()},
        wake=lambda: hdefereval.executeDeferred(holder["bridge"].pump), log=print,
    )
    holder["bridge"] = bridge
    bridge.start()
    _state["bridge"] = bridge
    return bridge
