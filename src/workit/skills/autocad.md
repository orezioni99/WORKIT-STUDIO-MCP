The script is **Python that runs next to the server** and drives AutoCAD through its
COM (ActiveX) object model. Each call is a fresh Python process: nothing you define
survives to the next call, but the drawing does. The same guide applies to BricsCAD,
ZWCAD, GstarCAD and nanoCAD, whose COM models copy AutoCAD's.

## Names already defined

| Name | What it is |
|---|---|
| `acad` | the Application object |
| `doc` | `acad.ActiveDocument` (None when no drawing is open) |
| `ms` | `doc.ModelSpace` |
| `point(x, y, z=0)` | a 3D point in the form COM needs |
| `doubles(...)` | array of doubles: `doubles([x1, y1, x2, y2, ...])` |
| `ints(list)`, `variants(list)` | arrays for selection-set filters |
| `objects(list)` | array of entities (for `AddRegion`, `CopyObjects`) |
| `command(text)` | type a command line, wait until AutoCAD is idle |
| `entities(space=None)` | list of every entity in model space |

**Always pass points and coordinate lists through `point()` / `doubles()`.** A plain
Python tuple fails with a type-mismatch error.

## Units

Drawing units are whatever the drawing says. Check before you draw:
`doc.GetVariable("INSUNITS")` (1 inch, 2 feet, 4 mm, 5 cm, 6 m) and
`doc.GetVariable("MEASUREMENT")` (0 imperial, 1 metric). Angles are radians.

## Recipes

```python
# inspect
result = {"file": doc.FullName, "entities": ms.Count,
          "layers": [doc.Layers.Item(i).Name for i in range(doc.Layers.Count)]}

# count entities by type
from collections import Counter
result = dict(Counter(e.ObjectName for e in entities()))

# draw
layer = doc.Layers.Add("A-WALL"); layer.color = 1          # ACI colour index
line = ms.AddLine(point(0, 0), point(5000, 0)); line.Layer = "A-WALL"
room = ms.AddLightWeightPolyline(doubles([0, 0, 6000, 0, 6000, 4000, 0, 4000]))  # 2D pairs
room.Closed = True
circle = ms.AddCircle(point(3000, 2000), 500)
text = ms.AddText("Living room", point(200, 200), 250)
acad.ZoomExtents()
result = {"area": room.Area}

# select by filter (all LINEs on layer A-WALL)
name = "OB_SEL"
try: doc.SelectionSets.Item(name).Delete()
except Exception: pass
sel = doc.SelectionSets.Add(name)
sel.Select(5, None, None, ints([0, 8]), variants(["LINE", "A-WALL"]))   # 5 = acSelectionSetAll
result = [sel.Item(i).Handle for i in range(sel.Count)]
sel.Delete()

# edit
obj = doc.HandleToObject("2B7")
obj.Move(point(0, 0), point(1000, 0)); obj.color = 3; obj.Update()

# blocks and attributes
ref = ms.InsertBlock(point(0, 0), "DOOR", 1, 1, 1, 0)
for att in ref.GetAttributes(): print(att.TagString, att.TextString)

# anything the object model lacks: use the command line
command('_.-LAYER _M A-DOOR _C 3  ')
```

## Traps

- `ObjectName` is the class (`AcDbLine`, `AcDbPolyline`, `AcDbBlockReference`,
  `AcDbText`, `AcDbMText`, `AcDbCircle`, `AcDbArc`, `AcDbHatch`).
- Collections are 0-based: `ms.Item(i)`, `doc.Layers.Item(i)`.
- `AddLightWeightPolyline` takes flat **2D** pairs; `AddPolyline` and `Add3DPoly` take
  flat 3D triples.
- Property reads that return points give a tuple of floats: `line.StartPoint`.
- `command()` is asynchronous inside AutoCAD; it waits for idle, but a command that asks
  for a click will hang. Always supply every answer in the string and use the `_.` and
  `_` prefixes so it works in every language version.
- If AutoCAD is busy (a command running, a dialog open) calls are retried for up to two
  minutes, then fail. Tell the user to press Esc in AutoCAD.
- Large drawings: iterating 100 000 entities over COM is slow. Use a selection-set
  filter instead of looping over model space.
- Civil 3D objects need its own COM library:
  `acad.GetInterfaceObject("AeccXUiLand.AeccApplication.13.6")` (13.6 = 2024, 13.7 = 2025).
- AutoCAD LT has no COM interface and cannot be driven this way.
- Saving: `doc.Save()` only when the user asked. `doc.SaveAs(path)` for a new file.
