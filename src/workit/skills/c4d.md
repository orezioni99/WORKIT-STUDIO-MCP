**Not yet run by the OmniBridge authors.** The script is **Python running inside Cinema
4D** on its main thread. Names you define stay available until Cinema 4D restarts.

## Names already defined

`c4d` and `doc` (the active document, refreshed before every script). `cad_modify`
opens and closes an undo group around the script and refreshes the interface after it.

## Units

Document units (default cm); rotations are radians (`c4d.utils.DegToRad`).

## Recipes

```python
# inspect
def walk(obj, depth=0, out=None):
    out = [] if out is None else out
    while obj:
        out.append(("  " * depth) + obj.GetName() + " [" + obj.GetTypeName() + "]")
        walk(obj.GetDown(), depth + 1, out); obj = obj.GetNext()
    return out
result = walk(doc.GetFirstObject())[:200]

# create (register each new object with the undo system)
cube = c4d.BaseObject(c4d.Ocube)
cube[c4d.PRIM_CUBE_LEN] = c4d.Vector(600, 300, 400)
cube.SetName("Room"); cube.SetAbsPos(c4d.Vector(0, 150, 0))
doc.InsertObject(cube); doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, cube)

# material
mat = c4d.BaseMaterial(c4d.Mmaterial); mat.SetName("Plaster")
mat[c4d.MATERIAL_COLOR_COLOR] = c4d.Vector(0.9, 0.9, 0.85)
doc.InsertMaterial(mat); doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, mat)
tag = cube.MakeTag(c4d.Ttexture); tag[c4d.TEXTURETAG_MATERIAL] = mat
```

## Traps

- Before changing an existing object call `doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)`.
- Vectors come back as text; return `[v.x, v.y, v.z]`.
- Cinema 4D 2026.4+ ships Maxon's own MCP server. Do not drive one scene with both.
