**Not yet run by the OmniBridge authors.** The script is **Python running inside
Autodesk Fusion** on its main thread (the `adsk` API). Names you define stay available
until the add-in stops.

## Names already defined

| Name | What it is |
|---|---|
| `adsk` | the API package (`adsk.core`, `adsk.fusion`, `adsk.cam`) |
| `app`, `ui` | Application and UserInterface |
| `design` | the active `adsk.fusion.Design` (None outside the Design workspace) |
| `root` | `design.rootComponent` |

`design`, `root` and `ui` are refreshed before every script, and any command the user
left running is ended first.

## Units

Internal lengths are **centimetres**, angles radians, whatever the document displays.
Build values with `adsk.core.ValueInput.createByString("25 mm")` to avoid mistakes.

## Recipes

```python
# inspect
result = {"document": app.activeDocument.name,
          "bodies": [b.name for b in root.bRepBodies],
          "parameters": [(p.name, p.expression) for p in design.userParameters]}

# sketch a rectangle and extrude it
sketch = root.sketches.add(root.xYConstructionPlane)
sketch.sketchCurves.sketchLines.addTwoPointRectangle(
    adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(6, 4, 0))        # cm
profile = sketch.profiles.item(0)
ext = root.features.extrudeFeatures
inp = ext.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
inp.setDistanceExtent(False, adsk.core.ValueInput.createByString("20 mm"))
body = ext.add(inp).bodies.item(0)
result = {"volume_cm3": body.volume}

# user parameter
design.userParameters.add("width", adsk.core.ValueInput.createByString("60 mm"), "mm", "")
design.userParameters.itemByName("width").expression = "80 mm"

# fit view
app.activeViewport.fit()
```

## Traps

- Collections use `.item(i)` (0-based) and `.count`; they are iterable.
- Never call `ui.messageBox` or `ui.selectEntity`: they wait for the user.
- Parametric versus direct design: timeline features exist only in parametric mode
  (`design.designType`).
- Fusion also ships Autodesk's own MCP server (Preferences > General > API). Use one
  or the other on a document.
