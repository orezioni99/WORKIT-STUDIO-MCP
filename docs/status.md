# What has actually been tested

**About this page.** Everything under "Run end to end" was done by the upstream
OmniBridge project before this fork was renamed to WORKIT STUDIO MCP. On the fork, as of
2026-11-17: the automated tests pass, the renamed command line runs, and nothing has
been run inside a real app yet.

Last updated 2026-11-15, version 0.1.0, on Windows 11 with Python 3.12 and the MCP
Python SDK 2.3.

## Run end to end

| What | How it was checked |
|---|---|
| MCP server over stdio | A real MCP client listed the five tools, read their annotations and called each one. |
| Wire protocol and in-app core | 14 automated tests against a fake host app: results, printed output, errors with traceback, main-thread execution, undo wrapping for modify only, token refusal, dropping of non-protocol (browser) requests, busy-app timeout, second-instance port, screenshot round trip. |
| Registry consistency | 53 automated tests: every app has a guide, every bridge file's port and id match the registry, every in-app bridge has an installer, bridge Python parses. |
| **AutoCAD 2024** | Attached to the running app; created a layer, a closed polyline, a circle, text and an arc; read them back (area 24.0 m² for a 6 x 4 m room); ran a command line; got a clear error for a bad call; captured the window. |
| **SOLIDWORKS 2025** (French install) | Attached; created a part; found a reference plane by type; sketched a 100 x 50 mm rectangle; extruded 20 mm; mass properties returned exactly 100 cm³; captured the window. |
| **Revit 2026** (French install, pyRevit Routes) | Extension registered with pyRevit; created and opened a new project; in one transaction created 76 levels, 76 floors and 602 walls (a 300 m tower, each floor turned 1.2 degrees, from an outline read back from AutoCAD); opened the 3D view; captured the window. |
| **Archicad 29** (with Tapir) | Read project info, stories and element counts; created 20 slabs (each turned 1.2 degrees, 4 m apart) and 8 columns through Tapir; counted them back; captured the window. |
| **Blender 5.2.4** | Add-on installed by `workit install blender` and enabled from the command line; bridge answered on port 47810; built 151 mesh objects (a 75-floor tower, each floor turned 1.2 degrees) in one undo step; changed the 3D view; saved a viewport render and a viewport screenshot. |
| **Unreal Engine 5.8** | Found the open editor by remote execution; spawned 151 actors (76 slabs and 75 floor volumes, each turned 1.2 degrees) in one editor transaction; moved the viewport camera; captured the window. |
| Window capture | AutoCAD, SOLIDWORKS, Revit and Unreal windows captured and scaled to PNG. |
| Installer | `install rhino` wrote its files and printed the startup line; `install blender` reported cleanly that Blender is not on the test PC. |

## Written but not yet run in the real app

These follow each vendor's documented API and share the tested core, but nobody has
run them in the application yet. Expect small fixes on first contact.

- In-app bridges: Rhino, 3ds Max, SketchUp, FreeCAD, Fusion, Maya, Cinema 4D, Houdini,
  QGIS. Rhino, 3ds Max and SketchUp are not installed on the test PC.
- COM apps other than AutoCAD and SOLIDWORKS: BricsCAD, ZWCAD, GstarCAD, nanoCAD,
  Inventor, CATIA, Solid Edge, MicroStation, ETABS, SAP2000, Robot.
- Tekla Structures (pythonnet).
- HTTP transport (`serve --transport http`): starts through the SDK, not yet called by
  a remote client.

## Known limits

- **Navisworks** uses the legacy COM API. It may fail to attach to a Navisworks the
  user started normally, and it cannot reach Clash Detective. A proper in-process
  plug-in is the next step for this app.
- **Archicad** cannot run code inside the app; scripts call JSON commands, and most
  creation commands need the Tapir add-on.
- **Scripts are not sandboxed** in any app.
- Windows only for COM apps and window capture. The in-app bridges are plain Python or
  Ruby and should work on macOS, but the installer paths are Windows paths.
- SketchUp's bridge is Ruby and could not even be syntax-checked on the test PC (no
  Ruby installed).
- The Cinema 4D plugin id is a placeholder and must be replaced by a registered one
  before distribution.
- **Revit, found on first contact:** a second Revit process (for example the hidden one
  kept warm by Autodesk's Personal Accelerator) can take Routes port 48884 first. The
  visible Revit then listens on 48885, and in one run its WORKIT STUDIO MCP routes were missing
  until Revit was restarted. Not yet understood.
- `cad_apps` reports AutoCAD as running while it is still loading; scripts fail for the
  first seconds with "not running". Retry after the app has finished starting.
- **Archicad, found on first contact:** creating elements on a story that is not the
  one on screen makes Archicad show an "elements created on unseen Stories" dialog. The
  elements are created, but every later command fails until the user clicks Continue.
- **Blender, found on first contact:** `workit install blender` needs Blender's
  settings folder, which a freshly unpacked Blender does not have until it has been
  started once. On a first start the splash screen covers the viewport screenshot.
