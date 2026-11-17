"""WorkitStudio add-on for Blender. Installed as the add-on folder `workit`
(this file plus workit_core.py). Enable it in Preferences > Add-ons."""

bl_info = {
    "name": "WorkitStudio",
    "author": "Workit Studio (based on OmniBridge)",
    "version": (0, 1, 0),
    "blender": (3, 2, 0),
    "location": "Runs in the background on 127.0.0.1:47810",
    "description": "Lets an AI assistant run scripts in Blender through the WORKIT STUDIO MCP server",
    "category": "System",
}

import bpy

from . import workit_core as core

PORT = 47810
_bridge = None


def _pump():
    if _bridge is not None:
        _bridge.pump()
    return 0.05


def _wrap(fn, label):
    value = fn()
    try:
        bpy.ops.ed.undo_push(message=label)
    except Exception:
        pass
    return value


def _view3d():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                region = next((r for r in area.regions if r.type == "WINDOW"), None)
                return window, area, region
    raise RuntimeError("no 3D viewport is open")


def _screenshot(path, width, height):
    window, area, region = _view3d()
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.screen.screenshot_area(filepath=path)


def _info():
    return {"version": bpy.app.version_string, "file": bpy.data.filepath or None}


def register():
    global _bridge
    _bridge = core.Bridge("blender", PORT, namespace={"bpy": bpy}, wrap=_wrap,
                          screenshot=_screenshot, info=_info, log=print)
    _bridge.start()
    if not bpy.app.timers.is_registered(_pump):
        bpy.app.timers.register(_pump, first_interval=0.5, persistent=True)


def unregister():
    global _bridge
    if bpy.app.timers.is_registered(_pump):
        bpy.app.timers.unregister(_pump)
    if _bridge is not None:
        _bridge.stop()
        _bridge = None
