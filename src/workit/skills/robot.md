**Not yet run by the OmniBridge authors.** The script is **Python that runs next to the
server** and drives Autodesk Robot Structural Analysis through its COM API (RobotOM).
Each call is a fresh Python process.

## Names already defined

`robot` (the Application), `project` (`robot.Project`), `structure`
(`project.Structure`), plus `nothing`, `VARIANT`, `doubles(...)`.

## Units

The API works in **SI base units**: metres, newtons, radians, whatever the interface shows.

## Recipes

```python
# inspect
nodes, bars = structure.Nodes, structure.Bars
result = {"file": project.FileName, "nodes": nodes.GetAll().Count,
          "bars": bars.GetAll().Count, "cases": structure.Cases.GetAll().Count}

# create nodes and a bar (modify)
nodes.Create(1, 0, 0, 0); nodes.Create(2, 6.0, 0, 0)
bars.Create(1, 1, 2)
robot.Project.ViewMngr.Refresh()

# calculate
project.CalcEngine.Calculate()
```

## Traps

- Object numbers are user numbers, not indices; collections from `GetAll()` are 1-based.
- Robot must have a project open; a results query before `Calculate()` returns zeros.
- Enumerations are plain integers over COM; look them up in the Robot API help.
