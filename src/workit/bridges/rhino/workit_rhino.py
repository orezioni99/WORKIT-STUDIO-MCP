#! python3
# -*- coding: utf-8 -*-
"""WorkitStudio for Rhino 7, 8 and 9 (and Grasshopper through Rhino).

Run once per Rhino session:   _-RunPythonScript "<this file>"
To load it automatically, add that line to
Options > General > "Run these commands every time Rhino starts".
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import Rhino
import System
import rhinoscriptsyntax as rs
import scriptcontext as sc

import workit_core as core

PORT = 47820


def _prepare(namespace):
    doc = Rhino.RhinoDoc.ActiveDoc
    sc.doc = doc
    namespace["doc"] = doc


def _wrap(fn, label):
    doc = Rhino.RhinoDoc.ActiveDoc
    serial = doc.BeginUndoRecord(label)
    try:
        return fn()
    finally:
        doc.EndUndoRecord(serial)


def _after(mode, ok):
    Rhino.RhinoDoc.ActiveDoc.Views.Redraw()


def _screenshot(path, width, height):
    view = Rhino.RhinoDoc.ActiveDoc.Views.ActiveView
    bitmap = view.CaptureToBitmap(System.Drawing.Size(width, height))
    bitmap.Save(path, System.Drawing.Imaging.ImageFormat.Png)


def _info():
    doc = Rhino.RhinoDoc.ActiveDoc
    return {"version": str(Rhino.RhinoApp.Version), "file": doc.Path if doc else None}


def start():
    holder = {}

    def wake():
        Rhino.RhinoApp.InvokeOnUiThread(System.Action(holder["bridge"].pump), None)

    bridge = core.Bridge(
        "rhino", PORT,
        namespace={"Rhino": Rhino, "rs": rs, "sc": sc, "System": System},
        prepare=_prepare, wrap=_wrap, after=_after, screenshot=_screenshot,
        wake=wake, info=_info, log=Rhino.RhinoApp.WriteLine,
    )
    holder["bridge"] = bridge
    bridge.start()
    return bridge


start()
