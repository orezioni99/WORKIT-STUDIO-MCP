# WORKIT STUDIO MCP

**One MCP server. Every scriptable CAD, BIM and 3D app. Any AI model.**

WORKIT STUDIO MCP lets Claude, ChatGPT, Gemini, Cursor, Copilot or a local model work inside
the design software on your PC: read the model, draw, edit, check, and look at the
result. It speaks the [Model Context Protocol](https://modelcontextprotocol.io), so any
MCP client can use it.

WORKIT STUDIO MCP is a fork of [OmniBridge MCP](https://github.com/ayoubmep/omnibridge-mcp)
adapted for work in Israel: see [Israel](#israel) and [Credits](#credits).

```
 Claude / ChatGPT / Gemini / Cursor / local model
                    |  MCP (stdio or HTTP)
              WORKIT STUDIO MCP server            5 tools, the same for every app
                    |
   +----------------+-----------------+----------------------+
   | in-app bridge  | automation      | the app's own channel|
   | (script runs   | (COM / .NET /   | (pyRevit Routes,     |
   |  inside)       |  JSON API)      |  Unreal remote exec) |
   +----------------+-----------------+----------------------+
   Blender, Rhino,   AutoCAD, SOLIDWORKS,  Revit, Unreal
   3ds Max, SketchUp Archicad, Navisworks,
   FreeCAD, Maya ... Inventor, Tekla ...
```

## The idea

pyRevit gave Revit a door for scripts. Tapir did the same for Archicad. WORKIT STUDIO MCP
applies that one principle everywhere: **do not wrap each app in hundreds of fixed
tools; give the model a way to run a short script in the app, and a guide for writing
that script well.**

So the server has five tools, whatever the app:

| Tool | What it does |
|---|---|
| `cad_apps` | lists every supported app and whether it is reachable right now |
| `cad_skill` | returns the scripting guide for one app: language, predefined names, units, recipes, traps |
| `cad_read` | runs a script that only inspects the model |
| `cad_modify` | runs a script that changes the model, as one undo step where the app allows |
| `cad_screenshot` | returns a picture of the app's viewport or window so the model can check its work |

Reading and changing are separate tools on purpose: MCP clients can auto-approve the
first and ask you before the second.

## Supported apps

"Tested" means the upstream OmniBridge authors ran it end to end, before this fork; none
of it has been re-run under the WORKIT STUDIO MCP name yet. Everything else is written against the
vendor's documented API and needs a first real run: please report what you find.

| App | How it connects | Script language | Status |
|---|---|---|---|
| **AutoCAD** (+ Civil 3D, Plant 3D, Map 3D, MEP) | COM automation, nothing to install | Python | **Tested** (AutoCAD 2024) |
| BricsCAD, ZWCAD, GstarCAD, nanoCAD | COM automation (AutoCAD-compatible) | Python | Untested |
| **Revit** | pyRevit extension (Routes) | Python (Revit API) | **Tested** (Revit 2026) |
| **Archicad** | JSON API + Tapir add-on | Python + `ac` helper | **Tested** (Archicad 29) |
| **Navisworks** Manage / Simulate | COM automation (legacy API) | Python | Experimental |
| **Rhino** 7 / 8 / 9 + Grasshopper | in-app Python bridge | Python | Untested |
| **3ds Max** 2021+ | in-app pymxs bridge | Python + MAXScript | Untested |
| **SketchUp** 2021+ | in-app Ruby bridge | Ruby | Untested |
| **Blender** 3.2+ | add-on | Python (bpy) | **Tested** (Blender 5.2) |
| FreeCAD 0.21+ | Mod folder bridge | Python | Untested |
| Autodesk Fusion | add-in | Python (adsk) | Untested |
| **SOLIDWORKS** | COM automation, nothing to install | Python | **Tested** (SOLIDWORKS 2025) |
| Inventor, CATIA V5, Solid Edge | COM automation | Python | Untested |
| MicroStation | COM automation | Python | Untested |
| Tekla Structures | Open API through pythonnet | Python | Untested |
| ETABS, SAP2000, Robot | COM automation | Python | Untested |
| Maya, Cinema 4D, Houdini | in-app Python bridge | Python | Untested |
| **Unreal Engine 5** | built-in Python remote execution | Python | **Tested** (UE 5.8) |
| QGIS 3.28+ / 4 | plugin | Python (PyQGIS) | Untested |

**Not possible today** (no scripting interface of any kind): Twinmotion, Lumion,
D5 Render, Enscape, Shapr3D, Plasticity, AutoCAD LT (no external automation),
Navisworks Freedom. Vectorworks, Allplan and NX only allow in-process plug-ins and are
on the roadmap.

## Install

Needs Windows and Python 3.10+. From a copy of this folder:

```bash
pip install -e .
```

Check what it can see:

```bash
workit apps
```

### Connect your AI client

```bash
workit config claude-desktop
```

prints the exact snippet for your machine. Replace the name with `claude-code`,
`cursor`, `vscode`, `gemini`, `codex`, `lmstudio`, `chatgpt` or `all`.
Details and caveats per client: [docs/clients.md](docs/clients.md).

### Connect your apps

Apps driven by automation (AutoCAD, SOLIDWORKS, Archicad, Tekla ...) need nothing:
start the app and open a file.

Apps that need a bridge inside them get it with one command:

```bash
workit install blender
```

Use `rhino`, `3dsmax`, `sketchup`, `freecad`, `fusion`, `maya`, `c4d`, `houdini`,
`qgis`, `revit`, or `all` for every app found on the PC. The command prints the one
manual step some apps still need (ticking the add-on, pasting a startup line).
`workit uninstall <app>` removes it again.

## Try it

Ask your AI client:

> Use WORKIT STUDIO MCP. Which CAD apps are open? In AutoCAD, draw a 6 x 4 m room on a new
> layer "A-WALL" with a 900 mm door opening on the south wall, then show me a
> screenshot.

More prompts, including cross-app ones: [examples/prompts.md](examples/prompts.md).

You can also drive an app from the terminal, which is handy for debugging:

```bash
workit run autocad "result = {'file': doc.Name, 'entities': ms.Count}"
```

## Safety

Giving an AI a script engine inside your design software is powerful. Treat it that way.

- **Local only.** Bridges listen on `127.0.0.1` and refuse any request without the
  secret token stored in `~/.workit/token`. A web page cannot read that file and
  cannot talk to the bridge.
- **Scripts are not sandboxed.** A script can do anything the app can do, including
  deleting geometry and writing files. Keep your client's approval prompt on for
  `cad_modify`, work on a copy of important models, and save before a session.
- **One undo step.** Where the app supports it, each `cad_modify` is a single undo
  entry named after what the AI said it was doing.
- **HTTP mode is for trusted networks.** `workit serve --transport http` has no
  login of its own. If you expose it through a tunnel for ChatGPT, use a tunnel that
  requires authentication and stop it afterwards.
- **Revit:** pyRevit Routes itself has no authentication; the WORKIT STUDIO MCP endpoints check
  the token, other Routes endpoints on your machine do not.

## How it works

- [docs/protocol.md](docs/protocol.md): the wire protocol and how to add an app (about
  60 lines of code for an app with a Python console).
- [docs/prior-art.md](docs/prior-art.md): the existing MCP servers for each app, the
  vendors' own servers, and how WORKIT STUDIO MCP differs. If one app is all you need, one of
  those dedicated servers may suit you better.
- [docs/status.md](docs/status.md): exactly what has been tested, and on what.

## Israel

Every guide returned by `cad_skill` ends with rules for working in Israel, and Revit,
AutoCAD (and its clones), SketchUp and QGIS have their own additions. They live in
`src/workit/skills/il/`, apart from the upstream guides, and cover:

- Hebrew names and text: pass them through unchanged, right-to-left display, fonts.
- Units: centimetres in architectural drawings, metres in site and survey drawings.
- Coordinates: Israel TM Grid (ITM, EPSG:2039) and the old grid (EPSG:28193).
- Regulations: the model measures and reports; it never states that a design complies.
- A short Hebrew to English glossary of building terms.

## Credits

WORKIT STUDIO MCP is based on [OmniBridge MCP](https://github.com/ayoubmep/omnibridge-mcp)
by the OmniBridge contributors, used under the MIT licence. The server, the bridges and
the upstream guides are their work; this fork renames the project and adds the Israeli
layer.

OmniBridge in turn stands on the ideas of [pyRevit](https://github.com/pyrevitlabs/pyRevit),
[Tapir](https://github.com/ENZYME-APD/tapir-archicad-automation),
[blender-mcp](https://github.com/ahujasid/blender-mcp),
[rhinomcp](https://github.com/jingcheng-chen/rhinomcp) and the many projects listed in
[docs/prior-art.md](docs/prior-art.md). No code from them is included.

## License

MIT. See [LICENSE](LICENSE).
