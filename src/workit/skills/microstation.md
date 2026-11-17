**Not yet run by the OmniBridge authors.** The script is **Python that runs next to the
server** and drives MicroStation through its COM object model (the MicroStation VBA
model). Each call is a fresh Python process.

## Names already defined

`ustn` (the Application), `dgn` (`ustn.ActiveDesignFile`), `model`
(`ustn.ActiveModelReference`), plus `nothing`, `VARIANT`, `doubles(...)`.

## Units

Coordinates are **master units** of the active model.

## Recipes

```python
# inspect
result = {"file": dgn.Name, "model": model.Name,
          "levels": [dgn.Levels.Item(i).Name for i in range(1, dgn.Levels.Count + 1)]}

# count elements by type
from collections import Counter
scan = model.Scan(nothing); counts = Counter()
while scan.MoveNext(): counts[scan.Current.Type] += 1
result = dict(counts)

# draw a line (modify)
p1 = ustn.Point3dFromXYZ(0, 0, 0); p2 = ustn.Point3dFromXYZ(10, 0, 0)
line = ustn.CreateLineElement2(nothing, p1, p2)
model.AddElement(line); line.Redraw()

# anything else: a key-in
ustn.CadInputQueue.SendKeyin("fit view extended")
```

## Traps

- Collections are 1-based.
- Key-ins that wait for a data point will hang; send the points with
  `CadInputQueue.SendDataPoint`.
- Bentley's newer in-app Python API is separate from this COM model.
