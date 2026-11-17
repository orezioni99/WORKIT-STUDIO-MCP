**Experimental.** The script is **Python that runs next to the server** and drives
Navisworks Manage or Simulate through its COM API. Autodesk calls this API legacy, and
it can only attach to a Navisworks that registered itself for automation, so expect
rough edges. Each call is a fresh Python process.

## Names already defined

| Name | What it is |
|---|---|
| `nw` | the `Navisworks.Document` automation object |
| `state` | `nw.State()`: the `InwOpState` object, root of the COM API |
| `nothing`, `VARIANT`, `doubles(...)` | COM helpers |

## Recipes

```python
# what is open
result = {"file": state.CurrentFileName, "partition": state.CurrentPartition.ObjectName}

# open or append a model (modify)
nw.OpenFile(r"C:\models\federated.nwd")
nw.AppendFile(r"C:\models\mep.nwc")

# saved viewpoints
views = state.SavedViews()
result = [views.Item(i).name for i in range(1, views.Count + 1)]     # COM collections are 1-based

# current selection: count and first item's properties
sel = state.CurrentSelection
paths = sel.Paths()
result = {"selected": paths.Count}
```

## Traps

- Collections in this API are **1-based**.
- Most of the modern feature set (Clash Detective results, search sets, the .NET
  object model) is **not** in the COM API. For clash reports, ask the user to export
  the clash report as XML or HTML and read that file instead.
- Navisworks Freedom has no API at all.
- If attaching fails, the running Navisworks was not started for automation. Say so
  rather than retrying.
