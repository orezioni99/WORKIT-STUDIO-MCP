**Not yet run by the OmniBridge authors.** The script is **Python that runs next to the
server** and drives Solid Edge through its COM API. Each call is a fresh Python process.

## Names already defined

`se` (the Application), `doc` (`se.ActiveDocument` or None), plus `nothing`, `VARIANT`,
`doubles(...)`.

## Units

The API works in **metres and radians**.

## Recipes

```python
# inspect
result = {"name": doc.Name, "type": doc.Type,          # 1 part, 3 assembly, 2 draft, 4 sheet metal
          "variables": [(v.Name, v.Value) for v in
                        (doc.Variables.Item(i) for i in range(1, doc.Variables.Count + 1))][:50]}

# change a variable (modify)
doc.Variables.Item("Length").Value = 0.25

# assembly occurrences
result = [doc.Occurrences.Item(i).Name for i in range(1, doc.Occurrences.Count + 1)]
```

## Traps

- Collections are 1-based.
- Solid Edge must have been started at least once to register its COM server.
- Some features (assembly pattern, mirror) refuse automation with "access denied".
