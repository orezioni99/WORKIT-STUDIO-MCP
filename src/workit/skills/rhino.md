The script is **Python running inside Rhino** on its UI thread (CPython 3 in Rhino 8
and 9, IronPython 2.7 in Rhino 7: avoid f-strings if `cad_apps` shows Python 2.7).
Names you define stay available in later calls until Rhino restarts.

## Names already defined

| Name | What it is |
|---|---|
| `Rhino` | RhinoCommon (`Rhino.Geometry`, `Rhino.DocObjects`, ...) |
| `rs` | `rhinoscriptsyntax` |
| `sc` | `scriptcontext` (`sc.doc` is the active document) |
| `doc` | `Rhino.RhinoDoc.ActiveDoc`, refreshed before every script |
| `System` | .NET `System` |

## Units

`rs.UnitSystemName()` and `doc.ModelAbsoluteTolerance`. Angles in `rs.*` are degrees;
in RhinoCommon they are radians.

## Recipes

```python
# inspect
result = {"units": rs.UnitSystemName(), "objects": len(rs.AllObjects() or []),
          "layers": rs.LayerNames()}

# create (rs returns GUIDs)
rs.AddLayer("Walls", (200, 60, 60))
box = rs.AddBox([(0,0,0),(6,0,0),(6,4,0),(0,4,0),(0,0,3),(6,0,3),(6,4,3),(0,4,3)])
rs.ObjectLayer(box, "Walls")
crv = rs.AddCircle((3, 2, 0), 1.0)
srf = rs.AddPlanarSrf([crv])
ext = rs.ExtrudeCurveStraight(crv, (0, 0, 0), (0, 0, 2.5))

# RhinoCommon for anything rs lacks
import Rhino.Geometry as rg
brep = rg.Sphere(rg.Point3d(0, 0, 0), 2.0).ToBrep()
guid = doc.Objects.AddBrep(brep)

# measure
result = {"volume": rs.SurfaceVolume(box)[0], "bbox": [list(p) for p in rs.BoundingBox(box)]}

# run a Rhino command (always scripted form: leading underscore and hyphen)
rs.Command('_-Zoom _Extents', echo=False)
```

## Grasshopper

Grasshopper is reachable from the same script:

```python
import clr; clr.AddReference("Grasshopper")
import Grasshopper
gh_doc = Grasshopper.Instances.ActiveCanvas.Document if Grasshopper.Instances.ActiveCanvas else None
result = [(o.NickName, o.GetType().Name) for o in gh_doc.Objects] if gh_doc else "Grasshopper is not open"
# set a slider and recompute
for o in gh_doc.Objects:
    if o.NickName == "Height": o.SetSliderValue(System.Decimal(3.5))
gh_doc.NewSolution(True)
```

## Traps

- `rs` functions return `None` on failure instead of raising: check return values.
- GUIDs come back as strings in the result; keep them to refer to objects later.
- Never call anything that waits for a pick (`rs.GetObject`, `rs.GetPoint`): it hangs.
  Work from `rs.AllObjects()`, `rs.ObjectsByLayer()`, `rs.SelectedObjects()`.
- Commands must be scripted (`_-Command` with every option given) or a dialog opens.
- The view redraws after each script; you do not need `rs.Redraw()`.
