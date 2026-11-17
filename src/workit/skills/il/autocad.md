## Units (Israel)

Many Israeli drawings have `INSUNITS` = 0 (unitless), so the variable does not tell you
the scale. Work it out before drawing:

- Architectural plans: usually 1 unit = **1 cm**.
- Survey maps (מפת מדידה), site and infrastructure plans: 1 unit = **1 m**, drawn at
  ITM coordinates (X around 120 000 to 290 000, Y around 370 000 to 800 000).
- Steel and shop details: often mm.

Check with something of known size, for example the measurement of an existing
dimension against its length, or a door opening (70 to 100 cm wide):

```python
dims = [e for e in entities() if e.ObjectName.endswith("Dimension")][:5]
result = {"insunits": doc.GetVariable("INSUNITS"),
          "dimlfac": doc.GetVariable("DIMLFAC"),
          "extmin": doc.GetVariable("EXTMIN"), "extmax": doc.GetVariable("EXTMAX"),
          "sample_dims": [round(d.Measurement, 2) for d in dims]}
```

If it is still unclear, ask the user. Do not change `INSUNITS` unless asked.

## Hebrew text and names (Israel)

- Layer, block and text-style names are often Hebrew. COM returns Unicode: use the
  names exactly as read from `doc.Layers`.
- New text is readable only in a text style whose font has Hebrew glyphs. Reuse a style
  the drawing already uses for Hebrew: find one by reading `StyleName` from existing
  Hebrew text, then set `text.StyleName = that_name`. Do not create a new style or
  change a style's font unless asked.
- Old drawings with SHX Hebrew fonts may store text in a legacy encoding, so
  `TextString` reads as Latin gibberish while the screen shows Hebrew. Report this to
  the user; do not rewrite such text.
- `AcDbMText.TextString` contains formatting codes (`\f...;`, `\P`). Strip them only in
  your report, never in the drawing.
- Write Hebrew in normal logical order. Never reverse the characters to "fix" the
  direction.
- In `command(...)` strings keep the `_.` and `_` prefixes, and put Hebrew layer names
  in the string as they are.

## Coordinates (Israel)

Geometry at ITM coordinates is normal and must stay there: never move a survey map to
the origin. To place something by coordinates, the order is X = east, Y = north. Check
`doc.GetVariable("UCSNAME")` and the UCS origin first; COM coordinates are WCS.
