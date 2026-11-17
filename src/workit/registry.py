"""Every app WorkitStudio knows, and how it is reached.

kind
    socket  a bridge add-in runs inside the app and executes the script there
    runner  the script runs in a helper process next to the server, with the
            app's automation objects (COM, .NET, HTTP) already connected
    revit   script runs inside Revit through a pyRevit Routes endpoint
    unreal  script runs inside Unreal Editor through Python remote execution
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class App:
    id: str
    name: str
    kind: str
    language: str
    port: int = 0
    runner: str = ""
    processes: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    skill: str = ""
    setup: str = ""
    family: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def skill_name(self) -> str:
        return self.skill or self.id


def _install(app_id: str, then: str) -> str:
    return f"Run `workit install {app_id}` once, then {then}"


APPS: tuple[App, ...] = (
    # ------------------------------------------------------------ in-app bridges
    App("blender", "Blender", "socket", "Python (bpy)", port=47810,
        processes=("blender.exe", "blender"),
        setup=_install("blender", "enable the WorkitStudio add-on in Preferences > Add-ons."),
        family="3D / DCC"),
    App("rhino", "Rhino + Grasshopper", "socket", "Python (RhinoCommon, rhinoscriptsyntax)",
        port=47820, processes=("rhino.exe", "rhinoceros"), aliases=("rhino3d", "grasshopper", "rhino8", "rhino7"),
        setup=_install("rhino", "restart Rhino (the installer prints the one startup command to paste)."),
        family="CAD"),
    App("3dsmax", "3ds Max", "socket", "Python (pymxs) and MAXScript", port=47830,
        processes=("3dsmax.exe",), aliases=("max", "3dmax", "3ds", "3dsmax"),
        setup=_install("3dsmax", "restart 3ds Max."), family="3D / DCC"),
    App("sketchup", "SketchUp", "socket", "Ruby (SketchUp API)", port=47840,
        processes=("sketchup.exe", "sketchup"), aliases=("su",),
        setup=_install("sketchup", "restart SketchUp."), family="CAD"),
    App("freecad", "FreeCAD", "socket", "Python (FreeCAD API)", port=47850,
        processes=("freecad.exe", "freecad"),
        setup=_install("freecad", "restart FreeCAD."), family="CAD"),
    App("maya", "Maya", "socket", "Python (maya.cmds)", port=47860,
        processes=("maya.exe", "maya"),
        setup=_install("maya", "restart Maya."), family="3D / DCC"),
    App("fusion", "Autodesk Fusion", "socket", "Python (adsk)", port=47870,
        processes=("fusion360.exe", "fusion.exe"), aliases=("fusion360",),
        setup=_install("fusion", "start the WorkitStudio add-in from Utilities > Add-Ins (it then runs on startup)."),
        family="Mechanical CAD"),
    App("c4d", "Cinema 4D", "socket", "Python (c4d)", port=47880,
        processes=("cinema 4d.exe",), aliases=("cinema4d",),
        setup=_install("c4d", "restart Cinema 4D."), family="3D / DCC"),
    App("houdini", "Houdini", "socket", "Python (hou)", port=47890,
        processes=("houdini.exe", "houdinifx.exe", "houdinicore.exe", "hindie.exe"),
        setup=_install("houdini", "restart Houdini."), family="3D / DCC"),
    App("qgis", "QGIS", "socket", "Python (PyQGIS)", port=47900,
        processes=("qgis-bin.exe", "qgis-ltr-bin.exe", "qgis"),
        setup=_install("qgis", "enable the WorkitStudio plugin in Plugins > Manage and Install Plugins."),
        family="GIS"),
    # ------------------------------------------------------- pyRevit / Unreal
    App("revit", "Revit", "revit", "Python (Revit API through pyRevit)", port=48884,
        processes=("revit.exe",),
        setup=_install("revit", "turn on Routes in pyRevit settings and reload pyRevit."),
        family="BIM"),
    App("unreal", "Unreal Engine", "unreal", "Python (unreal)", processes=("unrealeditor.exe",),
        aliases=("ue", "ue5", "unrealengine"),
        setup="In Unreal: enable the Python Editor Script Plugin, then Project Settings > "
              "Plugins > Python > Enable Remote Execution.",
        family="Real-time"),
    # ------------------------------------- out-of-process automation (no add-in)
    App("archicad", "Archicad", "runner", "Python with the `ac` helper (JSON API + Tapir)",
        runner="archicad", port=19723, processes=("archicad.exe",),
        setup="Open a project in Archicad. Install the Tapir add-on for the full command set.",
        family="BIM"),
    App("autocad", "AutoCAD (and Civil 3D, Plant 3D, Map 3D, MEP, Architecture)", "runner",
        "Python driving the AutoCAD COM object model", runner="com",
        processes=("acad.exe",), aliases=("acad", "civil3d", "plant3d", "autocadmep", "c3d"),
        setup="Start AutoCAD and open a drawing. AutoCAD LT has no COM API.",
        family="CAD", extra={"progids": ["AutoCAD.Application"]}),
    App("bricscad", "BricsCAD", "runner", "Python driving the AutoCAD-compatible COM model",
        runner="com", processes=("bricscad.exe",), skill="autocad",
        setup="Start BricsCAD and open a drawing.", family="CAD",
        extra={"progids": ["BricscadApp.AcadApplication"], "flavour": "autocad"}),
    App("zwcad", "ZWCAD", "runner", "Python driving the AutoCAD-compatible COM model",
        runner="com", processes=("zwcad.exe",), skill="autocad",
        setup="Start ZWCAD and open a drawing.", family="CAD",
        extra={"progids": ["ZWCAD.Application"], "flavour": "autocad"}),
    App("gstarcad", "GstarCAD", "runner", "Python driving the AutoCAD-compatible COM model",
        runner="com", processes=("gcad.exe",), skill="autocad",
        setup="Start GstarCAD and open a drawing.", family="CAD",
        extra={"progids": ["GCAD.Application"], "flavour": "autocad"}),
    App("nanocad", "nanoCAD", "runner", "Python driving the AutoCAD-compatible COM model",
        runner="com", processes=("ncad.exe",), skill="autocad",
        setup="Start nanoCAD and open a drawing.", family="CAD",
        extra={"progids": ["nanoCAD.Application"], "flavour": "autocad"}),
    App("navisworks", "Navisworks Manage / Simulate", "runner",
        "Python driving the Navisworks COM API", runner="com",
        processes=("roamer.exe",), aliases=("navis", "naviswork", "nwd"),
        setup="Start Navisworks Manage or Simulate and open a model. Freedom has no API.",
        family="BIM", extra={"progids": ["Navisworks.Document"], "flavour": "navisworks"}),
    App("solidworks", "SOLIDWORKS", "runner", "Python driving the SOLIDWORKS COM API",
        runner="com", processes=("sldworks.exe",), aliases=("sw", "solidwork"),
        setup="Start SOLIDWORKS.", family="Mechanical CAD",
        extra={"progids": ["SldWorks.Application"], "flavour": "solidworks"}),
    App("inventor", "Autodesk Inventor", "runner", "Python driving the Inventor COM API",
        runner="com", processes=("inventor.exe",),
        setup="Start Inventor.", family="Mechanical CAD",
        extra={"progids": ["Inventor.Application"], "flavour": "inventor"}),
    App("catia", "CATIA V5", "runner", "Python driving CATIA Automation (COM)",
        runner="com", processes=("cnext.exe",),
        setup="Start CATIA V5.", family="Mechanical CAD",
        extra={"progids": ["CATIA.Application"], "flavour": "catia"}),
    App("solidedge", "Solid Edge", "runner", "Python driving the Solid Edge COM API",
        runner="com", processes=("edge.exe",),
        setup="Start Solid Edge.", family="Mechanical CAD",
        extra={"progids": ["SolidEdge.Application"], "flavour": "solidedge"}),
    App("microstation", "MicroStation", "runner", "Python driving MicroStation COM (VBA model)",
        runner="com", processes=("ustation.exe", "microstation.exe"),
        setup="Start MicroStation and open a design file.", family="CAD",
        extra={"progids": ["MicroStationDGN.Application"], "flavour": "microstation"}),
    App("etabs", "CSI ETABS", "runner", "Python driving the CSI OAPI (COM)",
        runner="com", processes=("etabs.exe",),
        setup="Start ETABS and open a model.", family="Structural",
        extra={"progids": ["CSI.ETABS.API.ETABSObject"], "flavour": "csi"}),
    App("sap2000", "CSI SAP2000", "runner", "Python driving the CSI OAPI (COM)",
        runner="com", processes=("sap2000.exe",), skill="etabs",
        setup="Start SAP2000 and open a model.", family="Structural",
        extra={"progids": ["CSI.SAP2000.API.SapObject"], "flavour": "csi"}),
    App("robot", "Robot Structural Analysis", "runner", "Python driving the Robot COM API",
        runner="com", processes=("robot.exe",), aliases=("rsa",),
        setup="Start Robot Structural Analysis and open a model.", family="Structural",
        extra={"progids": ["Robot.Application"], "flavour": "robot"}),
    App("tekla", "Tekla Structures", "runner", "Python driving the Tekla Open API (.NET)",
        runner="tekla", processes=("teklastructures.exe",),
        setup="Start Tekla Structures and open a model. Needs `pip install pythonnet`.",
        family="BIM"),
)

_BY_ID = {app.id: app for app in APPS}
_ALIASES = {alias: app for app in APPS for alias in app.aliases}


def find(name: str) -> App:
    key = (name or "").strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    app = _BY_ID.get(key) or _ALIASES.get(key)
    if app is None:
        known = ", ".join(a.id for a in APPS)
        raise KeyError(f"Unknown app {name!r}. Known apps: {known}")
    return app
