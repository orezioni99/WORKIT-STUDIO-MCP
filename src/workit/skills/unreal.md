Run on Unreal Engine 5.8. The script is **Python running inside Unreal
Editor**, sent through Unreal's own Python remote execution (no plugin of ours). The
user must enable the Python Editor Script Plugin and
Project Settings > Plugins > Python > Enable Remote Execution.

## Names already defined

`unreal`. Globals you define persist in the editor's Python session. Return data with
`result = ...` only (the last-expression shortcut does not apply here). `cad_modify`
wraps the script in one editor transaction (one undo step).

## Units

Centimetres; rotations in degrees (`unreal.Rotator(pitch, yaw, roll)`). Z is up.

## Recipes

```python
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# inspect
result = [{"label": a.get_actor_label(), "class": a.get_class().get_name(),
           "location": [a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z]}
          for a in actors.get_all_level_actors()][:200]

# spawn a cube and scale it
cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
actor = actors.spawn_actor_from_object(cube, unreal.Vector(0, 0, 100), unreal.Rotator(0, 0, 0))
actor.set_actor_label("Room"); actor.set_actor_scale3d(unreal.Vector(6, 4, 3))
result = actor.get_path_name()

# assets
result = unreal.EditorAssetLibrary.list_assets("/Game", recursive=True)[:100]

# console command
unreal.SystemLibrary.execute_console_command(None, "stat fps")
```

## Traps

- Return plain values: Unreal objects come back as text.
- Asset operations (import, save, build lighting) can take minutes: raise `timeout_s`.
- Unreal 5.8 also ships Epic's own experimental MCP server on 127.0.0.1:8000.
- Never save, delete assets or switch levels unless asked.
