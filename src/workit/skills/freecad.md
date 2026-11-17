The script is **Python running inside FreeCAD** on its GUI thread. Names you define
stay available in later calls until FreeCAD restarts.

## Names already defined

`FreeCAD` (also `App`), `FreeCADGui` (also `Gui`), and `doc` = `FreeCAD.ActiveDocument`
(None when no document is open; refreshed before every script). Import workbench
modules yourself: `import Part, Sketcher, Draft, Arch`.

`cad_modify` wraps the script in one FreeCAD transaction (one undo step, aborted on
error) and recomputes the document afterwards.

## Units

Millimetres and degrees.

## Recipes

```python
# inspect
result = [{"name": o.Name, "label": o.Label, "type": o.TypeId} for o in doc.Objects]

# new document if none
doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("Model")

# primitives and booleans
import Part
box = doc.addObject("Part::Box", "Slab"); box.Length, box.Width, box.Height = 6000, 4000, 200
cyl = doc.addObject("Part::Cylinder", "Hole"); cyl.Radius, cyl.Height = 300, 200
cyl.Placement.Base = FreeCAD.Vector(3000, 2000, 0)
cut = doc.addObject("Part::Cut", "SlabWithHole"); cut.Base, cut.Tool = box, cyl
doc.recompute()
result = {"volume_mm3": cut.Shape.Volume, "valid": cut.Shape.isValid()}

# raw shapes
shape = Part.makeBox(100, 50, 20).fuse(Part.makeSphere(30))
Part.show(shape, "Blob")

# view
Gui.ActiveDocument.ActiveView.viewIsometric(); Gui.SendMsgToActiveView("ViewFit")

# export
Part.export([cut], r"C:\temp\slab.step")
```

## Traps

- `Name` is the unique internal id (ASCII, fixed); `Label` is what the user sees. Find
  objects with `doc.getObject(name)`.
- Call `doc.recompute()` before reading `Shape` of something you just changed, and
  check `obj.State` / `obj.isValid()` for errors afterwards.
- Sketch constraints are index-based and fragile; add geometry, then constraints,
  then recompute and check `sketch.solve()` returns 0.
- Vectors come back as text: return `list(v)` or `(v.x, v.y, v.z)`.
- Never close documents or call `FreeCAD.closeDocument` unless asked.
