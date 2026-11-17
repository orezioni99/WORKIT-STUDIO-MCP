# -*- coding: utf-8 -*-
"""WorkitStudio plugin for QGIS 3.28+ and 4.x."""
from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtCore import QTimer

from . import workit_core as core

PORT = 47900


class WorkitStudioPlugin(object):
    def __init__(self, iface):
        self.iface = iface
        self.bridge = None
        self.timer = None

    def _screenshot(self, path, width, height):
        self.iface.mapCanvas().saveAsImage(path)

    def initGui(self):
        import qgis.core

        self.bridge = core.Bridge(
            "qgis", PORT,
            namespace={"iface": self.iface, "QgsProject": QgsProject, "qgis": qgis,
                       "project": QgsProject.instance()},
            screenshot=self._screenshot, info={"version": Qgis.QGIS_VERSION},
        )
        self.bridge.start()
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.bridge.pump())
        self.timer.start(50)

    def unload(self):
        if self.timer is not None:
            self.timer.stop()
        if self.bridge is not None:
            self.bridge.stop()


def classFactory(iface):
    return WorkitStudioPlugin(iface)
