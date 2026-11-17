**Not yet run by the OmniBridge authors.** The script is **Python that runs next to the
server** and drives Tekla Structures through the Tekla Open API (.NET, loaded with
pythonnet). Each call is a fresh Python process.

## Names already defined

| Name | What it is |
|---|---|
| `model` | a connected `Tekla.Structures.Model.Model` |
| `tsm` | `Tekla.Structures.Model` |
| `tsg` | `Tekla.Structures.Geometry3d` |
| `ts` | `Tekla.Structures` |

`cad_modify` calls `model.CommitChanges()` for you when the script ends.

## Units

Millimetres and degrees.

## Recipes

```python
# inspect
info = model.GetInfo()
objs = model.GetModelObjectSelector().GetAllObjectsWithType(tsm.ModelObject.ModelObjectEnum.BEAM)
result = {"model": info.ModelName, "beams": objs.GetSize()}

# list profiles of the first 50 beams
out = []
while objs.MoveNext() and len(out) < 50:
    b = objs.Current
    out.append((b.Name, b.Profile.ProfileString, b.Material.MaterialString))
result = out

# create a beam (modify)
beam = tsm.Beam(tsg.Point(0, 0, 0), tsg.Point(6000, 0, 0))
beam.Profile.ProfileString = "HEA300"
beam.Material.MaterialString = "S355JR"
beam.Class = "3"
result = beam.Insert()
```

## Traps

- After changing an object's properties call `obj.Modify()`; new objects need `Insert()`.
- The Open API DLL version must match the running Tekla version; WORKIT STUDIO MCP loads the
  DLLs from the running Tekla's own folder.
- .NET enums and overloads: pass exact types (`tsg.Point`, not tuples).
- Needs `pip install pythonnet` in the environment that runs WORKIT STUDIO MCP.
