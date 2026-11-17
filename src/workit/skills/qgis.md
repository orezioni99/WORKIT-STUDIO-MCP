**Not yet run by the OmniBridge authors.** The script is **Python running inside QGIS**
(PyQGIS) on its main thread. Names you define stay available until the plugin reloads.

## Names already defined

`iface` (the QGIS interface), `QgsProject`, `project` (`QgsProject.instance()`), and
the `qgis` package (`from qgis.core import *` yourself for what you need).

## Recipes

```python
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField
from qgis.PyQt.QtCore import QVariant

# inspect
result = [{"name": l.name(), "type": l.type().name if hasattr(l.type(), "name") else int(l.type()),
           "crs": l.crs().authid(), "features": l.featureCount() if hasattr(l, "featureCount") else None}
          for l in project.mapLayers().values()]

# load a layer
layer = QgsVectorLayer(r"C:\gis\parcels.gpkg|layername=parcels", "Parcels", "ogr")
if layer.isValid(): project.addMapLayer(layer)

# memory layer with a point
mem = QgsVectorLayer("Point?crs=EPSG:4326", "Sites", "memory")
mem.dataProvider().addAttributes([QgsField("name", QVariant.String)]); mem.updateFields()
f = QgsFeature(mem.fields()); f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(-7.6, 33.57)))
f["name"] = "Casablanca"; mem.dataProvider().addFeatures([f]); project.addMapLayer(mem)

# processing
import processing
out = processing.run("native:buffer", {"INPUT": mem, "DISTANCE": 0.01, "OUTPUT": "memory:"})
project.addMapLayer(out["OUTPUT"])
iface.mapCanvas().zoomToFullExtent()
```

## Traps

- Always check `layer.isValid()`; a wrong path gives an invalid layer, not an error.
- Distances are in the layer CRS units (degrees for EPSG:4326): reproject first.
- Edits to file-backed layers need `layer.startEditing()` ... `layer.commitChanges()`.
- QGIS has no single undo step for a script; edits commit per layer.
