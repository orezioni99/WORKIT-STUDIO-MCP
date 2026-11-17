The script is **Ruby running inside SketchUp** on its UI thread (the SketchUp Ruby
API). The value of the last expression is the result; there is no `result` variable
convention here unless you end the script with it. Top-level variables and methods you
define persist until SketchUp restarts.

## Names you will use

`Sketchup.active_model` and from it `.entities`, `.selection`, `.layers`,
`.materials`, `.definitions`, `.active_view`. `Geom::Point3d`, `Geom::Vector3d`,
`Geom::Transformation`.

## Units

**Internal units are always inches**, whatever the model displays. Use the numeric
helpers: `3.m`, `250.mm`, `12.feet`. Convert results back: `length.to_m`, `length.to_mm`.
Areas are square inches: multiply by `0.00064516` for m².

## Recipes

```ruby
# inspect
model = Sketchup.active_model
{ "title" => model.title, "entities" => model.entities.size,
  "groups" => model.entities.grep(Sketchup::Group).map(&:name),
  "units" => model.options["UnitsOptions"]["LengthUnit"] }

# create a box as a group (always group new geometry)
model = Sketchup.active_model
group = model.entities.add_group
face = group.entities.add_face([0, 0, 0], [6.m, 0, 0], [6.m, 4.m, 0], [0, 4.m, 0])
face.reverse! if face.normal.z < 0
face.pushpull(3.m)
group.name = "Room"
group.material = "LightGray"
group.bounds.depth.to_m

# move, copy, delete
t = Geom::Transformation.translation([2.m, 0, 0])
group.transform!(t)
copy = group.copy
copy.erase!

# components
defn = model.definitions["Door"] || model.definitions.load("C:/lib/door.skp")
inst = model.entities.add_instance(defn, Geom::Transformation.new([1.m, 0, 0]))

# zoom
model.active_view.zoom_extents
nil
```

## Traps

- `cad_modify` wraps the script in one operation, so the user can undo it in one step
  and a failed script is rolled back. Do not call `start_operation` yourself.
- A face drawn on the ground plane faces down: `pushpull` then goes the wrong way.
  Check `face.normal` first, as in the recipe.
- Loose geometry sticks to whatever it touches. Always build inside a group or a
  component definition.
- Entities become invalid after erase or after an operation is undone: check
  `entity.valid?`.
- Return plain values. Entities come back as their `inspect` text; return
  `entity.persistent_id` (or `entityID`) to refer to them later, then find them with
  `model.find_entity_by_persistent_id(id)`.
- Never call `UI.messagebox`, `UI.inputbox` or a tool that waits for a click.
- `puts` output comes back as stdout.
