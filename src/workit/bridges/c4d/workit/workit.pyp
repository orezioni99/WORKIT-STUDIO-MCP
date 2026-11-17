# -*- coding: utf-8 -*-
"""WorkitStudio for Cinema 4D 2024 and later (folder: <prefs>/plugins/workit).

Cinema 4D 2026.4+ also ships Maxon's own MCP server; do not run both on one scene.
PLUGIN_ID is a placeholder: get a free unique id from developers.maxon.net
before distributing a build.
"""
import os
import sys

import c4d

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import workit_core as core

PORT = 47880
PLUGIN_ID = 1067421
_bridge = None


def _prepare(namespace):
    namespace["doc"] = c4d.documents.GetActiveDocument()


def _wrap(fn, label):
    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    try:
        return fn()
    finally:
        doc.EndUndo()


def _after(mode, ok):
    c4d.EventAdd()


class _Pump(c4d.plugins.MessageData):
    def GetTimer(self):
        return 100

    def CoreMessage(self, kind, data):
        if kind in (c4d.MSG_TIMER, PLUGIN_ID) and _bridge is not None:
            _bridge.pump()
        return True


if __name__ == "__main__":
    _bridge = core.Bridge("c4d", PORT, namespace={"c4d": c4d}, prepare=_prepare, wrap=_wrap,
                          after=_after, wake=lambda: c4d.SpecialEventAdd(PLUGIN_ID),
                          info={"version": str(c4d.GetC4DVersion())}, log=print)
    _bridge.start()
    c4d.plugins.RegisterMessagePlugin(id=PLUGIN_ID, str="WorkitStudio", info=0, dat=_Pump())
