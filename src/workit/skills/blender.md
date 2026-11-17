The script is **Python running inside Blender** on its main thread. Names you define
stay available in later calls until Blender restarts.

## Names already defined

`bpy`. Import anything else Blender ships (`mathutils`, `bmesh`, `math`).

## Units

Blender units are metres by default (`bpy.context.scene.unit_settings`). Rotations are
radians. Z is up.

## Recipes

```python
# inspect
result = [{"name": o.name, "type": o.type, "location": list(o.location),
           "dimensions": list(o.dimensions)} for o in bpy.context.scene.objects]

# create with the data API (works from any context, preferred)
import bmesh
mesh = bpy.data.meshes.new("Slab")
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(mesh); bm.free()
obj = bpy.data.objects.new("Slab", mesh)
bpy.context.scene.collection.objects.link(obj)
obj.scale = (6, 4, 0.2); obj.location = (3, 2, -0.1)

# material
mat = bpy.data.materials.new("Concrete"); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1)
obj.data.materials.append(mat)

# modifiers
mod = obj.modifiers.new("Bevel", "BEVEL"); mod.width = 0.02

# delete
bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
```

## Traps

- Scripts run from a timer, so `bpy.context` has no active area. Prefer `bpy.data`
  over `bpy.ops`. When you must use an operator that needs the 3D view, override:
  ```python
  win = bpy.context.window_manager.windows[0]
  area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
  region = next(r for r in area.regions if r.type == "WINDOW")
  with bpy.context.temp_override(window=win, area=area, region=region):
      bpy.ops.view3d.view_all()
  ```
- After changing data, `bpy.context.view_layer.update()` before reading
  `matrix_world` or `dimensions`.
- New objects must be linked to a collection or they are invisible.
- Names are not unique keys you choose: Blender appends `.001`. Read back `obj.name`.
- Rendering (`bpy.ops.render.render`) blocks Blender until it ends; raise `timeout_s`.
- Never call `bpy.ops.wm.quit_blender`, `read_homefile` or `open_mainfile` unless the
  user asked: they discard unsaved work.
- Blender 5.1+ uses Python 3.13; older versions 3.11. Do not rely on pip packages.
