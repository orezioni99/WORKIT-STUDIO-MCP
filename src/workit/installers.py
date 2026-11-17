"""Put each app's bridge where the app loads it from. Windows paths; every
function only touches folders that belong to the bridge (plus one marked block
in Maya's userSetup.py)."""
from __future__ import annotations

import glob
import json
import os
import shutil
from importlib import resources
from pathlib import Path

from . import adapters


class InstallError(RuntimeError):
    pass


def _source(*parts: str) -> Path:
    return Path(str(resources.files("workit").joinpath("bridges", *parts)))


CORE = ("_core", "workit_core.py")
MAYA_BEGIN = "# >>> WorkitStudio >>>"
MAYA_END = "# <<< WorkitStudio <<<"
MAYA_BLOCK = (f"{MAYA_BEGIN}\nimport maya.utils\n"
              "maya.utils.executeDeferred(\"import workit_maya; workit_maya.start()\")\n"
              f"{MAYA_END}\n")


def _appdata() -> Path:
    return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")


def _localappdata() -> Path:
    return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")


def _documents() -> Path:
    if os.name == "nt":
        try:
            import ctypes

            buffer = ctypes.create_unicode_buffer(260)
            if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buffer) == 0:
                return Path(buffer.value)
        except Exception:
            pass
    return Path.home() / "Documents"


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _stable(app: str) -> Path:
    """A fixed folder under ~/.workit for bridges that are loaded by path."""
    folder = adapters.home() / "bridges" / app
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _folders(pattern: str) -> list[Path]:
    return [Path(p) for p in sorted(glob.glob(pattern)) if os.path.isdir(p)]


def _need(found: list, what: str) -> None:
    if not found:
        raise InstallError(f"{what} was not found on this PC (start the app once, then retry).")


# ---------------------------------------------------------------- installers
def _blender() -> list[str]:
    roots = _folders(str(_appdata() / "Blender Foundation" / "Blender" / "*"))
    _need(roots, "A Blender settings folder")
    out = []
    for root in roots:
        target = root / "scripts" / "addons" / "workit"
        _copy(_source("blender", "__init__.py"), target / "__init__.py")
        _copy(_source(*CORE), target / "workit_core.py")
        out.append(f"[blender] installed in {target}")
    out.append("[blender] now enable it: Edit > Preferences > Add-ons > search 'WorkitStudio' > tick.")
    out.append("[blender] or from a terminal: blender -b --python-expr \"import bpy; "
               "bpy.ops.preferences.addon_enable(module='workit'); bpy.ops.wm.save_userpref()\"")
    return out


def _rhino() -> list[str]:
    folder = _stable("rhino")
    _copy(_source("rhino", "workit_rhino.py"), folder / "workit_rhino.py")
    _copy(_source(*CORE), folder / "workit_core.py")
    script = folder / "workit_rhino.py"
    return [
        f"[rhino] installed in {folder}",
        "[rhino] in Rhino: Tools > Options > General > 'Run these commands every time Rhino "
        "starts', paste this line, then restart Rhino:",
        f'        _-RunPythonScript "{script}"',
    ]


def _max() -> list[str]:
    folder = _stable("3dsmax")
    _copy(_source("max", "workit_max.py"), folder / "workit_max.py")
    _copy(_source(*CORE), folder / "workit_core.py")
    roots = _folders(str(_localappdata() / "Autodesk" / "3dsMax" / "*" / "ENU"))
    _need(roots, "A 3ds Max user folder")
    out = []
    for root in roots:
        stub = root / "scripts" / "startup" / "workit_startup.ms"
        stub.parent.mkdir(parents=True, exist_ok=True)
        stub.write_text(f'python.ExecuteFile @"{folder / "workit_max.py"}"\n', "utf-8")
        out.append(f"[3dsmax] startup script written to {stub}")
    out.append("[3dsmax] restart 3ds Max.")
    return out


def _sketchup() -> list[str]:
    roots = _folders(str(_appdata() / "SketchUp" / "SketchUp 20*" / "SketchUp"))
    _need(roots, "A SketchUp settings folder")
    out = []
    for root in roots:
        target = root / "Plugins" / "workit.rb"
        _copy(_source("sketchup", "workit.rb"), target)
        out.append(f"[sketchup] installed {target}")
    out.append("[sketchup] restart SketchUp.")
    return out


def _freecad() -> list[str]:
    base = _appdata() / "FreeCAD"
    if not base.is_dir():
        raise InstallError("A FreeCAD settings folder was not found (start FreeCAD once).")
    roots = [base] + _folders(str(base / "v*"))
    out = []
    for root in roots:
        target = root / "Mod" / "WorkitStudio"
        for name in ("InitGui.py", "workit_freecad.py"):
            _copy(_source("freecad", "WorkitStudio", name), target / name)
        _copy(_source(*CORE), target / "workit_core.py")
        out.append(f"[freecad] installed in {target}")
    out.append("[freecad] restart FreeCAD.")
    return out


def _maya() -> list[str]:
    scripts = _documents() / "maya" / "scripts"
    if not (scripts.parent).is_dir():
        raise InstallError("Documents/maya was not found (start Maya once).")
    _copy(_source("maya", "workit_maya.py"), scripts / "workit_maya.py")
    _copy(_source(*CORE), scripts / "workit_core.py")
    setup = scripts / "userSetup.py"
    text = setup.read_text("utf-8") if setup.exists() else ""
    if MAYA_BEGIN not in text:
        setup.write_text(text + ("\n" if text and not text.endswith("\n") else "") + MAYA_BLOCK,
                         "utf-8")
    return [f"[maya] installed in {scripts} and added a marked block to userSetup.py",
            "[maya] restart Maya."]


def _fusion() -> list[str]:
    roots = [p for p in (_appdata() / "Autodesk" / "Autodesk Fusion 360" / "API",
                         _appdata() / "Autodesk" / "Autodesk Fusion" / "API") if p.is_dir()]
    _need(roots, "The Fusion API folder")
    out = []
    for root in roots:
        target = root / "AddIns" / "WorkitStudio"
        for name in ("WorkitStudio.py", "WorkitStudio.manifest"):
            _copy(_source("fusion", "WorkitStudio", name), target / name)
        _copy(_source(*CORE), target / "workit_core.py")
        out.append(f"[fusion] installed in {target}")
    out.append("[fusion] in Fusion: Utilities > Add-Ins > WorkitStudio > Run (once).")
    return out


def _c4d() -> list[str]:
    roots = _folders(str(_appdata() / "Maxon" / "*"))
    roots = [r for r in roots if "cinema 4d" in r.name.lower()]
    _need(roots, "A Cinema 4D preferences folder")
    out = []
    for root in roots:
        target = root / "plugins" / "workit"
        _copy(_source("c4d", "workit", "workit.pyp"), target / "workit.pyp")
        _copy(_source(*CORE), target / "workit_core.py")
        out.append(f"[c4d] installed in {target}")
    out.append("[c4d] restart Cinema 4D.")
    return out


def _houdini() -> list[str]:
    folder = _stable("houdini")
    python = folder / "scripts" / "python"
    for name in ("workit_houdini.py", "uiready.py"):
        _copy(_source("houdini", "scripts", "python", name), python / name)
    _copy(_source(*CORE), python / "workit_core.py")
    roots = _folders(str(_documents() / "houdini*"))
    _need(roots, "A Houdini preferences folder (Documents/houdiniX.Y)")
    out = []
    for root in roots:
        package = root / "packages" / "workit.json"
        package.parent.mkdir(parents=True, exist_ok=True)
        package.write_text(json.dumps({"hpath": folder.as_posix()}, indent=2), "utf-8")
        out.append(f"[houdini] package written to {package}")
    out.append("[houdini] restart Houdini.")
    return out


def _qgis() -> list[str]:
    roots = (_folders(str(_appdata() / "QGIS" / "QGIS3" / "profiles" / "*"))
             + _folders(str(_appdata() / "QGIS" / "QGIS4" / "profiles" / "*")))
    _need(roots, "A QGIS profile folder")
    out = []
    for root in roots:
        target = root / "python" / "plugins" / "workit"
        for name in ("__init__.py", "metadata.txt"):
            _copy(_source("qgis", "workit", name), target / name)
        _copy(_source(*CORE), target / "workit_core.py")
        out.append(f"[qgis] installed in {target}")
    out.append("[qgis] in QGIS: Plugins > Manage and Install Plugins > Installed > tick WorkitStudio.")
    return out


def _revit() -> list[str]:
    folder = adapters.home() / "pyrevit"
    extension = folder / "WorkitStudio.extension"
    _copy(_source("revit", "WorkitStudio.extension", "startup.py"), extension / "startup.py")
    _copy(_source(*CORE), extension / "lib" / "workit_core.py")
    return [
        f"[revit] pyRevit extension written to {extension}",
        "[revit] register that folder with pyRevit, turn Routes on, then reload pyRevit:",
        f'        pyrevit extensions paths add "{folder}"',
        "        pyRevit tab > Settings > Routes > enable the Routes server",
    ]


_INSTALLERS = {
    "blender": _blender, "rhino": _rhino, "3dsmax": _max, "sketchup": _sketchup,
    "freecad": _freecad, "maya": _maya, "fusion": _fusion, "c4d": _c4d,
    "houdini": _houdini, "qgis": _qgis, "revit": _revit,
}

# Paths (globs) removed by uninstall. Only ever our own files and folders.
_REMOVE = {
    "blender": [("APPDATA", "Blender Foundation/Blender/*/scripts/addons/workit")],
    "rhino": [("HOME", "bridges/rhino")],
    "3dsmax": [("HOME", "bridges/3dsmax"),
               ("LOCALAPPDATA", "Autodesk/3dsMax/*/ENU/scripts/startup/workit_startup.ms")],
    "sketchup": [("APPDATA", "SketchUp/SketchUp 20*/SketchUp/Plugins/workit.rb")],
    "freecad": [("APPDATA", "FreeCAD/Mod/WorkitStudio"), ("APPDATA", "FreeCAD/v*/Mod/WorkitStudio")],
    "maya": [("DOCUMENTS", "maya/scripts/workit_maya.py"),
             ("DOCUMENTS", "maya/scripts/workit_core.py")],
    "fusion": [("APPDATA", "Autodesk/Autodesk Fusion*/API/AddIns/WorkitStudio")],
    "c4d": [("APPDATA", "Maxon/*/plugins/workit")],
    "houdini": [("HOME", "bridges/houdini"), ("DOCUMENTS", "houdini*/packages/workit.json")],
    "qgis": [("APPDATA", "QGIS/QGIS*/profiles/*/python/plugins/workit")],
    "revit": [("HOME", "pyrevit/WorkitStudio.extension")],
}


def installable() -> list[str]:
    return list(_INSTALLERS)


def install(app_id: str) -> list[str]:
    from .registry import find

    try:
        app = find(app_id)
    except KeyError as error:
        raise InstallError(str(error.args[0])) from None
    if app.id not in _INSTALLERS:
        return [f"[{app.id}] nothing to install: {app.setup}"]
    adapters.token()  # make sure the shared secret exists before any app starts
    return _INSTALLERS[app.id]()


def uninstall(app_id: str) -> list[str]:
    from .registry import find

    try:
        app = find(app_id)
    except KeyError as error:
        raise InstallError(str(error.args[0])) from None
    roots = {"APPDATA": _appdata(), "LOCALAPPDATA": _localappdata(),
             "DOCUMENTS": _documents(), "HOME": adapters.home()}
    out = []
    for root, pattern in _REMOVE.get(app.id, []):
        for path in glob.glob(str(roots[root] / pattern)):
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
            out.append(f"[{app.id}] removed {path}")
    if app.id == "maya":
        setup = _documents() / "maya" / "scripts" / "userSetup.py"
        if setup.exists():
            text = setup.read_text("utf-8")
            if MAYA_BEGIN in text and MAYA_END in text:
                start = text.index(MAYA_BEGIN)
                end = text.index(MAYA_END) + len(MAYA_END)
                setup.write_text(text[:start] + text[end:].lstrip("\n"), "utf-8")
                out.append("[maya] removed the WorkitStudio block from userSetup.py")
    if app.id == "revit":
        out.append(f'[revit] also run: pyrevit extensions paths forget "{adapters.home() / "pyrevit"}"')
    return out or [f"[{app.id}] nothing was installed"]
