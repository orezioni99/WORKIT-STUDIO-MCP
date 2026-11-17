**Not yet run by the OmniBridge authors.** The script is **Python running inside Maya**
on its main thread. Names you define stay available until Maya restarts.

## Names already defined

`cmds` (`maya.cmds`) and `mel` (`maya.mel`). Import `maya.api.OpenMaya as om` when you
need it. `cad_modify` wraps the script in one undo chunk.

## Units

`cmds.currentUnit(query=True, linear=True)` (default cm) and
`cmds.upAxis(query=True, axis=True)` (default Y up). Rotations are degrees.

## Recipes

```python
# inspect
shapes = cmds.ls(type="mesh") or []
result = {"scene": cmds.file(query=True, sceneName=True),
          "transforms": cmds.ls(transforms=True)[:100], "meshes": len(shapes)}

# create
cube = cmds.polyCube(width=600, depth=400, height=300, name="room")[0]
cmds.move(0, 150, 0, cube)
sphere = cmds.polySphere(radius=50, name="lamp")[0]
cmds.parent(sphere, cube)

# material
shader = cmds.shadingNode("lambert", asShader=True, name="plaster")
cmds.setAttr(shader + ".color", 0.9, 0.9, 0.85, type="double3")
cmds.select(cube); cmds.hyperShade(assign=shader)

# attributes, bounding box
cmds.setAttr(cube + ".translateX", 100)
result = cmds.exactWorldBoundingBox(cube)

# MEL when a command has no Python form
mel.eval("FrameAll;")
```

## Traps

- Most `cmds` creators return `[transform, historyNode]`: take `[0]`.
- `cmds.ls` returns `None`-safe lists only if you add `or []`.
- Names are not guaranteed: Maya renames on clashes. Use the returned name.
- Never call `cmds.file(new=True, force=True)` or open a scene unless asked.
- Do not open dialogs (`cmds.confirmDialog`, `cmds.fileDialog2`).
