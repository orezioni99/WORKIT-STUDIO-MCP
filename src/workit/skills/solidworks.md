The script is **Python that runs next to the server** and drives SOLIDWORKS through its
COM API (late-bound). Each call is a fresh Python process.

## Names already defined

| Name | What it is |
|---|---|
| `sw` | the `SldWorks` application object |
| `model` | `sw.ActiveDoc` (None when nothing is open) |
| `nothing` | a COM "Nothing" object: pass it where the API wants a null object |
| `VARIANT`, `pythoncom` | to build ByRef and array arguments |
| `doubles(...)` | array of doubles |

## Units

The API works in **metres, radians and kilograms**, whatever the document displays.

## Calling convention (important)

The link is late-bound COM. **A method that takes no arguments is called WITHOUT
parentheses**: `model.GetTitle`, `sw.RevisionNumber`, `feat.GetNextFeature`. Writing
`model.GetTitle()` fails with "'str' object is not callable". Methods with arguments
are called normally.

## Recipes

These were run on SOLIDWORKS 2025.

```python
# inspect
result = {"title": model.GetTitle, "path": model.GetPathName,
          "type": {1: "part", 2: "assembly", 3: "drawing"}.get(model.GetType)}

# feature tree
names, feat = [], model.FirstFeature
while feat is not None:
    names.append((feat.Name, feat.GetTypeName2))
    feat = feat.GetNextFeature
result = names

# new part (modify)
template = sw.GetUserPreferenceStringValue(8)            # 8 = default part template
part = sw.NewDocument(template, 0, 0, 0)
result = part.GetTitle

# sketch a rectangle on the first reference plane and extrude it 20 mm (modify)
plane, feat = None, model.FirstFeature
while feat is not None:
    if feat.GetTypeName2 == "RefPlane":                  # by type: names are localised
        plane = feat; break
    feat = feat.GetNextFeature
plane.Select2(False, 0)
model.SketchManager.InsertSketch(True)
model.SketchManager.CreateCornerRectangle(0, 0, 0, 0.1, 0.05, 0)        # metres
model.SketchManager.InsertSketch(True)
boss = model.FeatureManager.FeatureExtrusion3(True, False, False, 0, 0, 0.02, 0, False, False,
    False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False)
model.ViewZoomtofit2
result = boss.Name if boss is not None else "extrusion failed"

# mass properties
props = model.Extension.CreateMassProperty
result = {"volume_cm3": props.Volume * 1e6, "mass_kg": props.Mass}

# dimensions and rebuild
dim = model.Parameter("D1@Sketch1"); dim.SystemValue = 0.12
model.EditRebuild3
```

## Traps

- `SelectByID2`'s Callout argument must be `nothing`, never Python `None`.
- Output (ByRef) arguments such as the errors and warnings of `OpenDoc6` or `Save3`
  need `VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)`; read `.value` afterwards.
- Many calls return `None` on failure rather than raising. Check the return value.
- If SOLIDWORKS runs as administrator and the server does not (or the reverse),
  attaching fails. Both must run at the same level.
- Feature and plane names depend on the language of the install ("Front Plane" is
  "Plan de face" in French). Find things by type or read names from the feature tree;
  never assume English names in `SelectByID2`.
