## Units (Israel)

Israeli Revit templates usually display lengths in **centimetres**. Internal units are
still feet. Read the project's unit before you interpret the user's numbers:

```python
# Revit 2021 and newer
unit = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()
result = unit.TypeId            # contains "centimeters", "millimeters" or "meters"
cm = lambda v: DB.UnitUtils.ConvertToInternalUnits(v, DB.UnitTypeId.Centimeters)
to_cm = lambda v: DB.UnitUtils.ConvertFromInternalUnits(v, DB.UnitTypeId.Centimeters)
m = lambda v: DB.UnitUtils.ConvertToInternalUnits(v, DB.UnitTypeId.Meters)

# Revit 2020
result = str(doc.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits)
cm = lambda v: DB.UnitUtils.ConvertToInternalUnits(v, DB.DisplayUnitType.DUT_CENTIMETERS)
```

`app.VersionNumber` tells you which form to use. Report lengths in the project's unit
and areas in m².

## Hebrew names (Israel)

- Type, level, view, sheet, room and shared-parameter names are often Hebrew. Read the
  real names first, then use them exactly:
  `[l.Name for l in DB.FilteredElementCollector(doc).OfClass(DB.Level)]`.
- For built-in parameters use the `BuiltInParameter`, not the display name, so the
  script does not depend on naming:
  `w.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)`.
  `LookupParameter("...")` is for project and shared parameters, with the exact Hebrew
  name.
- Hebrew string literals work in the script as they are. Do not add `u""` prefixes or
  encode/decode calls.
- A TextNote or tag shows Hebrew correctly only when its type uses a font with Hebrew
  glyphs. Reuse a text type the project already uses for Hebrew instead of creating one.

## Coordinates (Israel)

Shared coordinates are normally set to ITM through the Survey Point; the model itself
sits near the internal origin. **Never place geometry at raw ITM coordinates**: Revit
loses accuracy beyond about 16 km from the internal origin. Convert instead:

```python
# ITM of the internal origin (metres) and the angle to true north
pos = doc.ActiveProjectLocation.GetProjectPosition(DB.XYZ.Zero)
ft = lambda v: DB.UnitUtils.ConvertFromInternalUnits(v, DB.UnitTypeId.Meters)
result = {"east": ft(pos.EastWest), "north": ft(pos.NorthSouth),
          "elevation": ft(pos.Elevation), "angle_rad": pos.Angle}

# ITM of any model point
p = doc.ActiveProjectLocation.GetProjectPosition(DB.XYZ(10, 5, 0))
```

If east and north come back as 0, shared coordinates were never set: say so rather than
reporting 0, 0 as a location.
