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
