**Not yet run by the OmniBridge authors.** The script is **Python that runs next to the
server** and drives Inventor through its COM API. Each call is a fresh Python process.

## Names already defined

`inv` (the Application), `doc` (`inv.ActiveDocument` or None), `tg`
(`inv.TransientGeometry`), plus `nothing`, `VARIANT`, `doubles(...)`.
`cad_modify` wraps the script in one Inventor transaction: one undo step, aborted on error.

## Units

Internal units are **centimetres and radians**, whatever the document displays.

## Recipes

```python
# inspect
result = {"name": doc.DisplayName, "type": doc.DocumentType,       # 12290 part, 12291 assembly
          "params": [(p.Name, p.Expression) for p in doc.ComponentDefinition.Parameters]}

# change a parameter (modify)
doc.ComponentDefinition.Parameters.Item("d0").Expression = "120 mm"
doc.Update()

# sketch and extrude in a part (modify)
cd = doc.ComponentDefinition
sketch = cd.Sketches.Add(cd.WorkPlanes.Item(3))                    # 3 = XY plane
sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(0, 0), tg.CreatePoint2d(10, 5))
profile = sketch.Profiles.AddForSolid()
ext = cd.Features.ExtrudeFeatures.CreateExtrudeDefinition(profile, 20481)   # 20481 = join
ext.SetDistanceExtent(2, 20993)                                    # 2 cm, positive direction
cd.Features.ExtrudeFeatures.Add(ext)
```

## Traps

- Collections are 1-based (`Item(1)`).
- Enumerations are plain integers over COM; look them up in the Inventor API help.
- Inventor 2027.2 ships Autodesk's own local MCP server; prefer one or the other.
