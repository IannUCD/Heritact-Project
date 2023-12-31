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
        def get_openstreetmap_category(x, y, raster_layer):
            geotransform = raster_layer.dataProvider().geotransform()
            longitude = geotransform[0] + (x * geotransform[1]) + (y * geotransform[2])
            latitude = geotransform[3] + (x * geotransform[4]) + (y * geotransform[5])
            bbox = (longitude - 0.001, latitude - 0.001, longitude + 0.001, latitude + 0.001)
            url = f"https://api.openstreetmap.org/api/0.6/map?bbox={','.join(map(str, bbox))}"
            response = requests.get(url)
            if response.status_code != 200:
                return "Unknown"
            root = ET.fromstring(response.content)
            for element in root:
                if element.tag == 'way':
                    category = 'Other'
                    for child in element:
                        if child.tag == 'tag':
                            category_tags = ['building', 'highway', 'waterway', 'landuse', 'leisure', 'amenity', 'natural', 'railway', 'power']
                            for tag in category_tags:
                                if child.attrib.get('k') == tag:
                                    category = child.attrib.get('v')
                                    break
                        if category != 'Other':
                            return category
                    return 'Other'

        def convert_to_heightmap():
            file_dialog = QFileDialog()
            file_paths, _ = file_dialog.getOpenFileNames(None, 'Select Raster Files', '', 'Raster Files (*.tif *.png *.jpg)')
            if not file_paths:
                return
            for file_path in file_paths:
                raster_layer = QgsRasterLayer(file_path, 'Raster Layer')
                if not raster_layer.isValid():
                    continue
                heightmap_layer = QgsRasterLayer('path_to_save_heightmap.tif', 'Heightmap')
                renderer = raster_layer.renderer()
                color_ramp_shader = renderer.clone()
                color_ramp_shader = color_ramp_shader.colorRamp()
                num_classes = color_ramp_shader.colorRampItemList()[0].numClasses()
                min_height = 0
                max_height = 255
                category_to_blue_mapping = {}
                for class_index in range(num_classes):
                    color_class = color_ramp_shader.colorRampItemList()[0].color(class_index)
                    red, _, _, _ = color_class.red(), color_class.green(), color_class.blue(), color_class.alpha()
                    height = min_height + ((max_height - min_height) * (red / 255))
                    openstreetmap_category = get_openstreetmap_category(heightmap_x, heightmap_y, raster_layer)
                    if openstreetmap_category not in category_to_blue_mapping:
                        blue_value = len(category_to_blue_mapping) * 20  # Adjust the increment as needed
                        category_to_blue_mapping[openstreetmap_category] = blue_value
                    blue_value = category_to_blue_mapping[openstreetmap_category]
                    heightmap_layer.dataProvider().setRasterPixelValue(heightmap_x, heightmap_y, [height, 0, blue_value])
                QgsProject.instance().addMapLayer(heightmap_layer)

        convert_to_heightmap()

def classFactory(iface):
    return HericraftPlugin(iface)
