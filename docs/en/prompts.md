# Prompts to try

[עברית](../../examples/prompts.md) · English

Start with "Use WORKIT STUDIO MCP." so the model reaches for the right tools.

## First contact

- Which CAD apps are open on my PC right now, and which could you control if I
  started them?

## AutoCAD

- In AutoCAD, draw a 6 x 4 m room on a new layer A-WALL with 200 mm thick walls and a
  900 mm door opening in the south wall. Show me a screenshot when done.
- Count every entity in this drawing by type and layer, and tell me which layers are
  empty.
- Find all text smaller than 2.5 mm and list where it is. Do not change anything.

## Revit

- How many walls, doors and windows does this model have per level?
- List every door whose Mark is empty, then fill them in as D-001, D-002 ... by level.
- Which rooms have no number? Do not change anything.

## Archicad

- Give me the project name, the stories with their elevations, and the number of
  elements of each type.
- Select every wall thinner than 10 cm so I can review them.

## Blender / Rhino / SketchUp / 3ds Max

- Build a simple table: a 1.6 x 0.8 m top, 40 mm thick, on four 50 mm square legs
  720 mm high. Then show me the viewport.
- Rhino: loft a surface through three circles of radius 2, 3 and 1 m at heights 0, 4
  and 8 m, and tell me its area.

## Across apps (the reason this is one server)

- Read the room names and areas from the open Revit model and write them as a table
  of text in a new AutoCAD drawing.
- Take the outline of the building footprint from AutoCAD and extrude it 9 m in
  Blender.
- Compare the number of columns in the Archicad project with the number in the Revit
  model and tell me which levels disagree.
