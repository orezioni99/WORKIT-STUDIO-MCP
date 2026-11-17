# How it works, and how to add an app

## Three ways to reach an app

| Kind | Where the script runs | Used for |
|---|---|---|
| `socket` | inside the app, on its main thread | apps with their own script engine: Blender, Rhino, 3ds Max, SketchUp, FreeCAD, Maya, Fusion, Cinema 4D, Houdini, QGIS |
| `runner` | in a short-lived helper process next to the server, with the app's automation objects already connected | apps with an outside automation interface: AutoCAD and other COM apps, Archicad (JSON API), Tekla (.NET) |
| `revit`, `unreal` | inside the app, through a channel the app already has | pyRevit Routes, Unreal Python remote execution |

Every app is one entry in `src/workit/registry.py`.

## The in-app bridge protocol

One request per TCP connection, on `127.0.0.1` only. One line of JSON each way.

Request:

```json
{"token": "...", "id": "ab12", "op": "exec", "code": "result = 1 + 1",
 "mode": "read", "label": "AI: add walls", "timeout": 120}
```

- `op`: `ping`, `exec` or `screenshot` (`path`, `width`, `height`).
- `mode`: `read` or `modify`. Only `modify` is wrapped in the host's undo step.
- `token`: the contents of `~/.workit/token`. A request without it is refused. A
  request that is not valid JSON on its first line is dropped without an answer, so a
  browser cannot smuggle one in.

Response:

```json
{"id": "ab12", "ok": true, "result": 2, "stdout": "", "elapsed_ms": 3}
{"id": "ab12", "ok": false, "error": "NameError: ...", "traceback": "...", "stdout": ""}
```

The result is the script's `result` variable if it sets one, otherwise the value of
its last expression. Values JSON cannot carry come back as their `repr`.

Ports: each app has a base port (Blender 47810, Rhino 47820, 3ds Max 47830,
SketchUp 47840, FreeCAD 47850, Maya 47860, Fusion 47870, Cinema 4D 47880,
Houdini 47890, QGIS 47900). A second instance of the same app takes the next port, up
to five. `cad_apps` lists them and every tool takes an optional `instance` port.

## The main-thread problem

Every one of these apps requires its API to be called from its main thread, while a
network request arrives on another thread. `workit_core.py` (one dependency-free
file, Python 2.7 to 3.13) solves this once:

- the socket thread only parses the request and puts a job in a queue;
- the host shim makes the app call `bridge.pump()` on its main thread, either from a
  timer (Blender `bpy.app.timers`, Qt `QTimer` in 3ds Max, FreeCAD, QGIS) or on demand
  through a `wake` callback (Rhino `InvokeOnUiThread`, Maya `executeDeferred`, Fusion
  custom events, Cinema 4D `SpecialEventAdd`, Houdini `hdefereval`);
- the socket thread waits for the job and sends the answer.

A `ping` is answered by the socket thread itself, so an app that is busy still shows
as connected.

## Adding an app with a Python console

1. Write a shim of about 60 lines next to the others in `src/workit/bridges/`:

   ```python
   import workit_core as core
   bridge = core.Bridge(
       "myapp", 47910,
       namespace={"api": the_apps_module},     # names scripts can use
       wrap=run_inside_one_undo_step,           # optional: wrap(fn, label)
       screenshot=save_viewport_png,            # optional: (path, width, height)
       wake=schedule_pump_on_main_thread,       # or call bridge.pump() from a timer
   )
   bridge.start()
   ```
2. Add an `App(...)` entry with `kind="socket"` and the same port to `registry.py`.
3. Add an installer in `installers.py` that copies the shim and `workit_core.py`
   into the app's auto-load folder.
4. Write `skills/myapp.md`: names, units, five recipes, the traps you hit.
5. Run `pytest`: the consistency tests check that the port, the app id, the skill and
   the installer all agree.

## Adding a COM app

Add an `App(...)` entry with `runner="com"` and its ProgID, plus a small "flavour"
function in `runners/com.py` that names the objects scripts get. The runner attaches
to the running app, registers a COM message filter so a busy app is retried rather
than failing with "call was rejected by callee", runs the script and exits.

## Tests

```bash
pytest
```

The protocol tests use a fake host: a plain thread that plays an app's main thread.
They need no CAD software.
