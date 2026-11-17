The script is **Python running inside Revit** through pyRevit (IronPython), in a valid
Revit API context. Names you define stay available until pyRevit reloads.

## Names already defined

| Name | What it is |
|---|---|
| `doc` | the active Document |
| `uidoc` | the active UIDocument (selection, active view) |
| `uiapp`, `app` | UIApplication and Application |
| `DB` | `Autodesk.Revit.DB` |
| `UI` | `Autodesk.Revit.UI` |

## Transactions

- `cad_read`: no transaction. Any change raises an error.
- `cad_modify`: the whole script runs inside **one Transaction** named after your
  summary. If the script raises, everything is rolled back. **Do not start your own
  Transaction.** Call `doc.Regenerate()` when later lines need geometry created by
  earlier lines.

## Units

Internal length is **decimal feet**, angles radians. Convert:

```python
mm = lambda v: DB.UnitUtils.ConvertToInternalUnits(v, DB.UnitTypeId.Millimeters)
to_mm = lambda v: DB.UnitUtils.ConvertFromInternalUnits(v, DB.UnitTypeId.Millimeters)
```
(Revit 2021 and older use `DB.DisplayUnitType.DUT_MILLIMETERS`.)

## Recipes

```python
# inspect
walls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls) \
          .WhereElementIsNotElementType().ToElements()
result = {"title": doc.Title, "walls": len(walls),
          "levels": [(l.Name, to_mm(l.Elevation)) for l in
                     DB.FilteredElementCollector(doc).OfClass(DB.Level)]}

# parameters
w = walls[0]
result = {p.Definition.Name: p.AsValueString() for p in w.Parameters}
w.LookupParameter("Comments").Set("checked by AI")            # modify only

# create a wall (modify)
level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
line = DB.Line.CreateBound(DB.XYZ(0, 0, 0), DB.XYZ(mm(6000), 0, 0))
wall = DB.Wall.Create(doc, line, level.Id, False)
result = wall.Id.ToString()

# selection and view
ids = [e.ToString() for e in uidoc.Selection.GetElementIds()]
view = doc.ActiveView
```

## Traps

- Element ids: return `element.Id.ToString()`. Build one back with
  `DB.ElementId(int(text))` (Revit 2024+: `DB.ElementId(System.Int64(text))`).
- IronPython: no f-strings on IronPython 2.7; use `"{}".format(x)`.
- .NET lists: `System.Collections.Generic.List[DB.ElementId](ids)` where the API wants
  `ICollection<ElementId>`.
- Collectors are lazy and can be huge: count or filter, never return every element.
- Never call `TaskDialog.Show` or anything that waits for the user.
- Worksharing: an element owned by another user cannot be edited; report it.
- pyRevit 7 also ships its own MCP server (`pyrevit mcp`). Both can be installed; use
  one at a time on a model.
