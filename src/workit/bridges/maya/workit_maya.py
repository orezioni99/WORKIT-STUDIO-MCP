# -*- coding: utf-8 -*-
"""WorkitStudio for Maya 2022 and later (lives in Documents/maya/scripts).

userSetup.py starts it with:
    import maya.utils
    maya.utils.executeDeferred("import workit_maya; workit_maya.start()")
"""
import maya.cmds as cmds
import maya.mel as mel
import maya.utils

import workit_core as core

PORT = 47860
_state = {}


def _wrap(fn, label):
    cmds.undoInfo(openChunk=True, chunkName=label)
    try:
        return fn()
    finally:
        cmds.undoInfo(closeChunk=True)


def _screenshot(path, width, height):
    cmds.playblast(completeFilename=path, format="image", compression="png",
                   frame=cmds.currentTime(query=True), viewer=False, showOrnaments=False,
                   widthHeight=(width, height), percent=100, forceOverwrite=True)


def start():
    if _state.get("bridge"):
        return _state["bridge"]
    holder = {}
    bridge = core.Bridge(
        "maya", PORT, namespace={"cmds": cmds, "mel": mel},
        wrap=_wrap, screenshot=_screenshot,
        info={"version": cmds.about(version=True)}, log=print,
        wake=lambda: maya.utils.executeDeferred(holder["bridge"].pump),
    )
    holder["bridge"] = bridge
    bridge.start()
    _state["bridge"] = bridge
    return bridge
