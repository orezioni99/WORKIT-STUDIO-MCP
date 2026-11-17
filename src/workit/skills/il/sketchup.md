## Units (Israel)

Israeli models usually display **centimetres** or metres. Internal units stay inches,
so always build with the helpers (`20.cm`, `2.8.m`) and report with `.to_cm` / `.to_m`.
Read the display unit first:

```ruby
opts = Sketchup.active_model.options["UnitsOptions"]
{ "format" => opts["LengthFormat"], "unit" => opts["LengthUnit"] }
# LengthUnit: 0 inches, 1 feet, 2 mm, 3 cm, 4 m
```

Report areas in m² (square inches times `0.00064516`).

## Hebrew names (Israel)

- Tag (layer), group, component, material and scene names are often Hebrew. Ruby
  strings are UTF-8: use the names exactly as read, for example
  `Sketchup.active_model.layers.map(&:name)`.
- Hebrew string literals work in the script as they are. Do not call `force_encoding`
  or `reverse`.
- 3D text and dimension text in Hebrew depend on the font. After adding any, check with
  `cad_screenshot` and tell the user if it looks wrong instead of trying to mirror it.

## Location (Israel)

SketchUp stores latitude and longitude, not ITM. Read what the model has:

```ruby
model = Sketchup.active_model
si = model.shadow_info
{ "georeferenced" => model.georeferenced?, "lat" => si["Latitude"],
  "lon" => si["Longitude"], "north_angle" => si["NorthAngle"] }
```

Israel lies roughly between latitude 29.5 and 33.3 north, longitude 34.2 and 35.9 east.
Values outside that range mean the location was never set: say so before running any
shadow or sun study. Do not change the location unless asked.
