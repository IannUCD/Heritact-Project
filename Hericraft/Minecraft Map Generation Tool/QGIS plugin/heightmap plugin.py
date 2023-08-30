import rasterio
import requests
import xml.etree.ElementTree as ET
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsRasterLayer, QgsProject
from qgis.utils import iface

class HeightmapPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        # Define your icon path here
        icon_path = 'icons/icon.png'

        self.action = QAction(QIcon(icon_path), 'Convert to Heightmap', self.iface.mainWindow())
        self.action.triggered.connect(self.convert_to_heightmap)
        
        # Add the action to the toolbar
        self.iface.addToolBarIcon(self.action)

        # Add the action to the plugin menu
        self.iface.addPluginToMenu('&Heightmap Plugin', self.action)

    def unload(self):
        # Remove the action from the toolbar
        self.iface.removeToolBarIcon(self.action)

    def get_openstreetmap_category(self, x, y, raster_layer):
        # Get the raster's geotransform (georeferencing information)
        geotransform = raster_layer.dataProvider().geotransform()
        
        # Calculate latitude and longitude from pixel coordinates using the geotransform
        longitude = geotransform[0] + (x * geotransform[1]) + (y * geotransform[2])
        latitude = geotransform[3] + (x * geotransform[4]) + (y * geotransform[5])

        # Define the bounding box for the OpenStreetMap query
        bbox = (longitude - 0.001, latitude - 0.001, longitude + 0.001, latitude + 0.001)
        
        # Make a request to the OpenStreetMap API to retrieve data for the specified bounding box
        url = f"https://api.openstreetmap.org/api/0.6/map?bbox={','.join(map(str, bbox))}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return "Unknown"
        
        # Parse the OpenStreetMap XML response
        root = ET.fromstring(response.content)
        
        for element in root:
            if element.tag == 'way':
                category = 'Other'
                
                for child in element:
                    if child.tag == 'tag':
                        # Check for various OpenStreetMap tags to determine the category
                        category_tags = ['building', 'highway', 'waterway', 'landuse', 'leisure', 'amenity', 'natural', 'railway', 'power']
                        for tag in category_tags:
                            if child.attrib.get('k') == tag:
                                category = child.attrib.get('v')
                                break
                
                if category != 'Other':
                    return category
        
        return 'Other'

    def convert_to_heightmap(self):
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

                openstreetmap_category = self.get_openstreetmap_category(heightmap_x, heightmap_y, raster_layer)

                if openstreetmap_category not in category_to_blue_mapping:
                    blue_value = len(category_to_blue_mapping) * 20  # Adjust the increment as needed
                    category_to_blue_mapping[openstreetmap_category] = blue_value

                blue_value = category_to_blue_mapping[openstreetmap_category]

                heightmap_layer.dataProvider().setRasterPixelValue(heightmap_x, heightmap_y, [height, 0, blue_value])

            QgsProject.instance().addMapLayer(heightmap_layer)

# ... (classFactory and other methods)
