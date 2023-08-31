pip install rasterio
import rasterio
import requests
import xml.etree.ElementTree as ET
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsRasterLayer, QgsProject
from qgis.utils import iface
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QAction

class HericraftPlugin(QObject):

    def __init__(self, iface):
        super().__init__()
        self.iface = iface

    def initGui(self):
        self.action = QAction("Hericraft Plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("Plugins", self.action)

    def unload(self):
        self.iface.removePluginMenu("Plugins", self.action)

    def run(self):
        # Your plugin functionality here
        pass

def classFactory(iface):
    return HericraftPlugin(iface)
