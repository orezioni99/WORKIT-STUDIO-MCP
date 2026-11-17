**Not yet run by the OmniBridge authors.** The script is **Python that runs next to the
server** and drives CSI ETABS or SAP2000 through the CSI OAPI (COM). Each call is a
fresh Python process.

## Names already defined

`etabs` (the ETABSObject / SapObject), `sap` and `SapModel` (both `etabs.SapModel`),
plus `VARIANT`, `doubles(...)`.

## Conventions of the OAPI

- Almost every function returns a status code where **0 means success**. Functions with
  output arguments return a tuple or list: the outputs first or last depending on the
  COM binding, with the status code among them. Print the raw return once to see its
  shape before you rely on positions.
- Set the units you want first, then everything is in those units:
  `sap.SetPresentUnits(6)` (6 = kN, m, C; 5 = kN, mm, C; 4 = kip, ft, F).

## Recipes

```python
# inspect
result = {"file": sap.GetModelFilename(), "units": sap.GetPresentUnits(),
          "frames": sap.FrameObj.Count(), "areas": sap.AreaObj.Count(),
          "stories": sap.Story.GetNameList()}

# load cases and combos
result = {"patterns": sap.LoadPatterns.GetNameList(), "combos": sap.RespCombo.GetNameList()}

# add a frame between two points (modify; unlock first)
sap.SetModelIsLocked(False)
out = sap.FrameObj.AddByCoord(0, 0, 0, 0, 0, 3.0, "", "Default", "", "Global")
sap.View.RefreshView(0, False)
result = out

# run and read reactions
sap.Analyze.RunAnalysis()
sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
sap.Results.Setup.SetCaseSelectedForOutput("Dead")
result = sap.Results.JointReact("", 2)        # 2 = selection-independent: all objects
```

## Traps

- The model must be **unlocked** to edit; running the analysis locks it again.
- `RunAnalysis` on an unsaved model fails: the model needs a file path.
- Analysis can take minutes: raise `timeout_s`.
- Large result arrays: summarise (maxima, counts) rather than returning them whole.
