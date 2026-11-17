The script is **Python running inside 3ds Max** (pymxs) on its main thread. Names you
define stay available in later calls until 3ds Max restarts.

## Names already defined

| Name | What it is |
|---|---|
| `rt` | `pymxs.runtime`: every MAXScript global, class and function |
| `pymxs` | the module (`pymxs.undo`, `pymxs.animate`, `pymxs.attime`) |
| `mxs(code)` | run a MAXScript string and return its value |

## Units

System units: `rt.units.SystemType` and `rt.units.SystemScale`. Display units differ
from system units; geometry values are always system units. Angles are degrees.

## Recipes

```python
# inspect
result = [{"name": o.name, "class": str(rt.classOf(o)), "pos": [o.pos.x, o.pos.y, o.pos.z]}
          for o in rt.objects]

# create
box = rt.Box(length=400, width=600, height=300, name="Room")
box.pos = rt.Point3(0, 0, 0)
sphere = rt.Sphere(radius=50, pos=rt.Point3(100, 0, 300), segs=32)
box.wirecolor = rt.Color(200, 80, 80)

# modifiers and materials
rt.addModifier(box, rt.Shell(outerAmount=20))
mat = rt.PhysicalMaterial(name="Plaster"); mat.base_color = rt.Color(230, 230, 220)
box.material = mat

# transform, select, delete
rt.move(box, rt.Point3(0, 0, 100)); rt.rotate(box, rt.EulerAngles(0, 0, 45))
rt.select(box); rt.delete(sphere)

# anything easier in MAXScript
mxs('for o in geometry where o.material == undefined collect o.name')
```

## Traps

- MAXScript `undefined` arrives as Python `None`; MAXScript arrays are 1-based when you
  index them through `rt`, but iterate like Python lists.
- Name-value keywords are plain keyword arguments: `rt.Box(length=10)`.
- MAXScript names with dots or symbols need `rt.execute` / `mxs()`.
- `rt.objects` is live; copy it (`list(rt.objects)`) before deleting while iterating.
- Results that are Max values (Point3, Matrix3, nodes) come back as text: convert to
  lists of floats yourself.
- Do not start a render that opens the frame buffer and waits; use
  `rt.render(outputfile=..., vfb=False)`.
- Never reset or load a scene (`rt.resetMaxFile`, `rt.loadMaxFile`) unless asked.
