# Prior art

Surveyed on 2026-11-14. Stars and licences are from the GitHub API on that day and will
drift. "No licence file" means the repository cannot legally be reused as-is, whatever
its README says. WORKIT STUDIO MCP includes no code from any of these projects.

## What changed in 2026: vendors now ship their own servers

| Vendor server | Status | Notes |
|---|---|---|
| Blender Lab MCP (`projects.blender.org/lab/blender_mcp`) | Released, Blender 5.1+ | GPL-3.0, includes generic `execute_blender_code` |
| McNeel RhinoAI (`github.com/mcneel/rhinoai`) | In Rhino 9 beta; Rhino 8 via Package Manager | MIT, Grasshopper 1 and 2, runs scripts |
| Maxon Cinema 4D MCP Server | Built into 2026.4+ | Off by default, token auth, `exec_python` |
| Epic Unreal MCP plugin | Experimental, UE 5.8 | HTTP only on 127.0.0.1:8000, no stdio |
| Autodesk Fusion MCP | Generally available | Local HTTP on 127.0.0.1:27182 |
| Autodesk Revit Public MCP Server | Technical preview, Revit 2027.2 only | Fixed tools, no code execution |
| Autodesk AutoCAD / Civil 3D MCP | Inside the app | Only usable from Autodesk Assistant |
| Autodesk Inventor MCP | Announced with 2027.2 | Local |
| Graphisoft Archicad MCP | Beta, Archicad 30, paid plans | stdio |
| pyRevit Agent Runtime (`pyrevit mcp`) | Shipped in pyRevit 7.0 | Named pipe, `run_query` / `run_modify` |
| Trimble SketchUp Connector | Released | Cloud only: does not drive desktop SketchUp |
| IfcOpenShell `ifcopenshell-mcp` | 0.9.0 | Headless IFC editing, no app needed |
| Bentley MicroStation MCP | Early access | Restricted users |

**Where WORKIT STUDIO MCP fits:** these servers are each tied to one app, often to its newest
version and sometimes to a paid plan or a single AI client. WORKIT STUDIO MCP gives one
uniform interface across apps and versions (AutoCAD 2024, Revit 2023, Archicad 25,
Blender 3.x ...) and across clients. Where a vendor server exists and fits your
version, it is a good choice for that app; the two can be installed side by side, but
drive a given model with one at a time.

## Community servers by app

### AutoCAD and clones
- [daobataotie/CAD-MCP](https://github.com/daobataotie/CAD-MCP): MIT, ~700 stars. pywin32 COM for AutoCAD, GstarCAD, ZWCAD.
- [puran-water/autocad-mcp](https://github.com/puran-water/autocad-mcp): MIT, ~650 stars. AutoLISP dispatcher with file IPC, which is how it reaches AutoCAD LT.
- [AnCode666/multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp): Apache-2.0. AutoCAD, ZWCAD, GstarCAD, BricsCAD.

### Revit
- [mcp-servers-for-revit/mcp-servers-for-revit](https://github.com/mcp-servers-for-revit/mcp-servers-for-revit): MIT, ~450 stars. C# add-in, WebSocket.
- [mcp-servers-for-revit/mcp-server-for-revit-python](https://github.com/mcp-servers-for-revit/mcp-server-for-revit-python): MIT. pyRevit Routes, the same channel WORKIT STUDIO MCP uses.
- [Sam-AEC/aec-model-bridge](https://github.com/Sam-AEC/aec-model-bridge): GPL-3.0. Large tool set.

### Archicad
- [ENZYME-APD/tapir-archicad-automation](https://github.com/ENZYME-APD/tapir-archicad-automation): MIT. The add-on WORKIT STUDIO MCP calls.
- [SzamosiMate/tapir-archicad-MCP](https://github.com/SzamosiMate/tapir-archicad-MCP): MIT. Generated Tapir commands behind list / schema / call tools.
- [lgradisar/archicad-mcp](https://github.com/lgradisar/archicad-mcp): MIT.

### Navisworks
- [HorizunGroup/naviscoord-mcp](https://github.com/HorizunGroup/naviscoord-mcp): MIT. .NET add-in, 53 tools.
- [bimwright/nwd-mcp](https://github.com/bimwright/nwd-mcp): Apache-2.0. In-process plug-in with C# execution. This in-process route reaches Clash Detective, which WORKIT STUDIO MCP's COM route cannot.

### Rhino and Grasshopper
- [jingcheng-chen/rhinomcp](https://github.com/jingcheng-chen/rhinomcp): MIT, ~1.2k stars. C# plug-in, script execution, Grasshopper tools.

### 3ds Max
- [cl0nazepamm/3dsmax-mcp](https://github.com/cl0nazepamm/3dsmax-mcp): MIT, ~390 stars. Native C++ plug-in, 160+ tools.

### SketchUp
- [mhyrr/sketchup-mcp](https://github.com/mhyrr/sketchup-mcp): ~550 stars, no licence file. Ruby extension, `eval_ruby`.
- [zinin/sketchup-mcp2](https://github.com/zinin/sketchup-mcp2): MIT. Timer-driven Ruby server, the same threading approach WORKIT STUDIO MCP uses.

### Blender
- [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp): MIT, ~34k stars. The project that popularised the add-on + socket pattern.

### FreeCAD, Fusion, SOLIDWORKS, Inventor, CATIA
- [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp): MIT, ~3.3k stars.
- [faust-machines/fusion360-mcp-server](https://github.com/faust-machines/fusion360-mcp-server): MIT.
- [eyfel/mcp-server-solidworks](https://github.com/eyfel/mcp-server-solidworks): AGPL-3.0. [vespo92/SolidworksMCP-TS](https://github.com/vespo92/SolidworksMCP-TS): MIT.
- [NeonGlay/inventor-mcp](https://github.com/NeonGlay/inventor-mcp): MIT.
- [daiemon12/catia-v5-mcp-server](https://github.com/daiemon12/catia-v5-mcp-server): MIT.

### Structural, Tekla, GIS
- [rclab-auth/csi-mcp](https://github.com/rclab-auth/csi-mcp): MIT. ETABS and SAP2000.
- [teknovizier/tekla_mcp_server](https://github.com/teknovizier/tekla_mcp_server): GPL-3.0.
- [nkarasiak/qgis-mcp](https://github.com/nkarasiak/qgis-mcp): GPL-2.0.

### Maya, Cinema 4D, Houdini, Unreal
- [PatrickPalmer/MayaMCP](https://github.com/PatrickPalmer/MayaMCP): MIT.
- [ttiimmaacc/cinema4d-mcp](https://github.com/ttiimmaacc/cinema4d-mcp): MIT.
- [healkeiser/fxhoudinimcp](https://github.com/healkeiser/fxhoudinimcp): MIT.
- [runreal/unreal-mcp](https://github.com/runreal/unreal-mcp): MIT. Uses Python remote execution, as WORKIT STUDIO MCP does.

### Multi-app projects
- The `dcc-mcp` GitHub organisation publishes adapters for Maya, 3ds Max, Houdini and Cinema 4D.
- [Cai-aa/CAD-Agent-Hub](https://github.com/Cai-aa/CAD-Agent-Hub): MIT. CATIA, SOLIDWORKS, NX, Fusion.

## Design choices WORKIT STUDIO MCP took from this survey

- **Own port range (47810-47909).** Port 9876 is the default of at least five other
  projects (Blender, SketchUp, Houdini, FreeCAD, Fusion), so they collide.
- **A token on every bridge.** Most community bridges accept any local connection.
- **Script execution as the main interface.** The vendors' own servers (Blender, Rhino,
  Cinema 4D, Fusion) all ended up exposing it too.
- **COM where it exists.** AutoCAD, SOLIDWORKS, Inventor and the others need nothing
  installed in the app.
