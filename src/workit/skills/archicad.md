Archicad has no script engine to send code to. The script is **Python that runs next to
the server** and calls Archicad through the `ac` helper: Archicad's built-in JSON API
plus the commands of the Tapir add-on. Each call is a fresh Python process.

## Names already defined

| Name | What it does |
|---|---|
| `ac.cmd(name, parameters=None)` | run a built-in command, e.g. `"API.GetAllElements"`; returns its `result` |
| `ac.tapir(name, parameters=None)` | run a Tapir command, e.g. `"GetProjectInfo"`; returns its response |
| `ac.has_tapir()` | True when the Tapir add-on is loaded |
| `ac.guids(elements)` | flatten an element list to guid strings |
| `ArchicadError` | raised when a command fails (message says why) |

Element lists always look like `[{"elementId": {"guid": "..."}}, ...]` and commands
take them back in the same shape.

## Units

Metres and radians in the API, whatever the project displays.

## Recipes

```python
# inspect (built-in API)
info = ac.cmd("API.GetProductInfo")
walls = ac.cmd("API.GetElementsByType", {"elementType": "Wall"})["elements"]
result = {"version": info["version"], "walls": len(walls)}

# properties
ids = ac.cmd("API.GetPropertyIds", {"properties": [
    {"type": "BuiltIn", "nonLocalizedName": "General_ElementID"}]})["properties"]
values = ac.cmd("API.GetPropertyValuesOfElements",
                {"elements": walls[:20], "properties": ids})["propertyValuesForElements"]

# Tapir: project, details, creation
project = ac.tapir("GetProjectInfo")
details = ac.tapir("GetDetailsOfElements", {"elements": walls[:10]})
stories = ac.tapir("GetStories")
ac.tapir("CreateColumns", {"columnsData": [
    {"coordinates": {"x": 0.0, "y": 0.0, "z": 0.0}}, {"coordinates": {"x": 5.0, "y": 0.0, "z": 0.0}}]})
selected = ac.tapir("GetSelectedElements")["elements"]
```

## Finding commands

Built-in commands are documented at archicadapi.graphisoft.com/JSONInterfaceDocumentation
and Tapir's at enzyme-apd.github.io/tapir-archicad-automation/archicad_addon. If you are
unsure a Tapir command exists, ask Archicad:

```python
result = ac.cmd("API.IsAddOnCommandAvailable", {"addOnCommandId":
    {"commandNamespace": "TapirCommand", "commandName": "CreateSlabs"}})
```

Do not guess parameter names. When a command fails the error text names the missing or
wrong field: read it and correct.

## Traps

- Without Tapir only the built-in API works: it reads elements, properties,
  classifications, navigator and layouts, but creates almost nothing. If
  `ac.has_tapir()` is False, say so and point the user to the Tapir add-on.
- Each command is its own undo step in Archicad; there is no way to group them.
- Archicad must have a project open and no modal dialog showing.
- Creating elements above or below the story on screen (a slab with `level` 12 while
  the Ground Floor is shown) makes Archicad open an "elements created on unseen
  Stories" dialog. The elements exist, but the call hangs and later commands fail with
  "Invalid program status" until the user clicks Continue. Warn the user before
  building on several stories, and ask them to tick "Don't show this dialog again".
- Recipes run on Archicad 29: `CreateSlabs` takes `{"slabsData": [{"level": z,
  "polygonCoordinates": [{"x": .., "y": ..}, ...]}]}`.
- Several Archicad instances: `cad_apps` cannot tell them apart yet; pass
  `instance=<port>` (19723, 19724, ...).
- Archicad 30 has Graphisoft's own MCP server on paid plans; this bridge works from
  Archicad 25 on any licence.
