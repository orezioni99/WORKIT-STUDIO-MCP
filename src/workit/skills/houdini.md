**Not yet run by the OmniBridge authors.** The script is **Python running inside
Houdini** on its main thread. Names you define stay available until Houdini restarts.

## Names already defined

`hou`. `cad_modify` wraps the script in one undo group.

## Recipes

```python
# inspect
result = {"hip": hou.hipFile.path(), "frame": hou.frame(),
          "obj": [(n.name(), n.type().name()) for n in hou.node("/obj").children()]}

# build a small network
obj = hou.node("/obj")
geo = obj.createNode("geo", "room")
box = geo.createNode("box"); box.parmTuple("size").set((6, 3, 4))
bevel = geo.createNode("polybevel"); bevel.setInput(0, box); bevel.parm("offset").set(0.05)
bevel.setDisplayFlag(True); bevel.setRenderFlag(True)
geo.layoutChildren()
result = {"points": len(bevel.geometry().points()), "path": bevel.path()}

# parameters and errors
node = hou.node("/obj/room/box1")
result = {"parms": {p.name(): p.eval() for p in node.parms()[:40]}, "errors": node.errors()}
```

## Traps

- Refer to nodes by path; `createNode` may rename on clashes, so read `node.path()`.
- Cooking heavy networks blocks Houdini: raise `timeout_s`.
- Check `node.errors()` and `node.warnings()` after wiring; a red node does not raise.
- Do not call `hou.ui.displayMessage` or other dialogs.
- Never `hou.hipFile.clear()` or load a file unless asked.
