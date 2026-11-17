## Coordinate systems (Israel)

- National grid: **EPSG:2039** (Israel TM Grid, רשת ישראל החדשה), metres.
- Old grid: **EPSG:28193** (Israel / Israeli CS, רשת ישראל הישנה). Still found in old
  files. Never assume one for the other.
- Web maps and GPS: EPSG:4326 (lat/lon) and EPSG:3857.

Read before you act, and reproject instead of relabelling:

```python
result = {"project": QgsProject.instance().crs().authid(),
          "layers": {l.name(): l.crs().authid()
                     for l in QgsProject.instance().mapLayers().values()}}

# transform a point from lat/lon to ITM
tr = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"),
                            QgsCoordinateReferenceSystem("EPSG:2039"),
                            QgsProject.instance())
p = tr.transform(QgsPointXY(34.78, 32.08))        # x = longitude, y = latitude
result = [round(p.x(), 2), round(p.y(), 2)]
```

A layer with no CRS whose coordinates look like ITM (see the ranges in the common
rules) is probably EPSG:2039, but ask the user before assigning it. `setCrs` only
relabels a layer; it does not move the data.

## Hebrew attributes (Israel)

- Layer names, field names and values are often Hebrew. Use them exactly as read.
- Shapefiles from Israeli sources often have no `.cpg` file and are encoded in
  Windows-1255, so Hebrew shows as gibberish. Fix the reading, not the data:

```python
layer.setProviderEncoding("windows-1255")     # try "UTF-8" if that is not it
layer.dataProvider().reloadData()
```

- Measure areas and lengths in EPSG:2039 (metres, m²; 1 dunam / דונם = 1 000 m²), not
  in a lat/lon CRS.
