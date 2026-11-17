**Not yet run by the OmniBridge authors.** The script is **Python that runs next to the
server** and drives CATIA V5 through CATIA Automation (COM), the same object model CATIA
VBA macros use. Each call is a fresh Python process.

## Names already defined

`catia` (the Application), `doc` (`catia.ActiveDocument` or None), plus `nothing`,
`VARIANT`, `doubles(...)`.

## Units

Lengths are **millimetres**, angles degrees.

## Recipes

```python
# inspect
result = {"name": doc.Name, "path": doc.FullName,
          "windows": [catia.Windows.Item(i).Caption for i in range(1, catia.Windows.Count + 1)]}

# part: parameters
part = doc.Part
result = [(p.Name, p.ValueAsString()) for p in
          (part.Parameters.Item(i) for i in range(1, part.Parameters.Count + 1))][:50]

# new part with a pad (modify)
new = catia.Documents.Add("Part"); part = new.Part
body = part.MainBody
sketch = body.Sketches.Add(part.OriginElements.PlaneXY)
f2d = sketch.OpenEdition()
f2d.CreateClosedCircle(0, 0, 25)
sketch.CloseEdition()
pad = part.ShapeFactory.AddNewPad(sketch, 40)
part.Update()
```

## Traps

- Collections are 1-based (`Item(1)`); `Item("name")` also works.
- Always call `part.Update()` after changes, and check for update errors.
- Record a macro in CATIA to discover the calls for an unfamiliar operation; the VBA
  it produces maps line for line to Python.
- 3DEXPERIENCE CATIA uses the same ProgID; if both are installed you get whichever
  registered last.
