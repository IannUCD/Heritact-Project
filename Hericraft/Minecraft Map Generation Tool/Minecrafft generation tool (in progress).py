# ## Dependencies

# ### These code lines have to be executed inside your python powershell

pip install Pillow pymclevel

# ## The code

# # Image Processing

# Step 1: Import necessary libraries
from PIL import Image
import pymclevel
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


from PIL import Image

def calculate_coordinates(x, y, geotransform):
    # Extract geotransform values
    origin_x = geotransform[0]
    pixel_width = geotransform[1]
    rotation_x = geotransform[2]
    origin_y = geotransform[3]
    rotation_y = geotransform[4]
    pixel_height = geotransform[5]

    # Calculate latitude and longitude
    longitude = origin_x + (x * pixel_width) + (y * rotation_x)
    latitude = origin_y + (x * rotation_y) + (y * pixel_height)

    return latitude, longitude
    print(f"Pixel ({x}, {y}) corresponds to Latitude: {latitude}, Longitude: {longitude}")


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
            # Handle error cases
            return "Unknown"
        
        # Parse the OpenStreetMap XML response
        root = ET.fromstring(response.content)
        
                # Iterate through the elements in the XML response (nodes)
        for element in root:
            # Check if the element represents a way (e.g., a road, building, etc.)
            if element.tag == 'way':
                # Initialize category to 'Other' as a default
                category = 'Other'
                
                # Iterate through the child elements of the way
                for child in element:
                    if child.tag == 'tag':
                        # Check for various OpenStreetMap tags to determine the category
                        if child.attrib.get('k') == 'building':
                            category = 'Building'
                        elif child.attrib.get('k') == 'highway':
                            category = 'Road'
                        elif child.attrib.get('k') == 'waterway':
                            category = 'Water'
                        elif child.attrib.get('k') == 'landuse':
                            category = 'Land Use'
                        elif child.attrib.get('k') == 'leisure':
                            category = 'Leisure'
                        elif child.attrib.get('k') == 'amenity':
                            category = 'Amenity'
                        elif child.attrib.get('k') == 'natural':
                            category = 'Natural'
                        elif child.attrib.get('k') == 'railway':
                            category = 'Railway'
                        elif child.attrib.get('k') == 'power':
                            category = 'Power'
                        #Add more categories
                
                # Return the determined category if it's not 'Other'
                if category != 'Other':
                    return category
        
        # If no relevant features are found, return 'Other' as a fallback
        return 'Other'


def get_category_color(category):
    global category_colors
    
    if category not in category_colors:
        # Assign a new blue value for the category
        next_blue_value = max(category_colors.values(), default=0) + 1
        category_colors[category] = (0, 0, next_blue_value)
    
    return category_colors.get(category, (0, 0, 0))  # Default to black for unknown categories

# Define a dictionary to store category colors
category_colors = {}


from PIL import Image
import requests
import xml.etree.ElementTree as ET
import rasterio

def convert_to_heightmap(input_raster_path, output_image_path):
    with rasterio.open(input_raster_path) as src:
        width = src.width
        height = src.height
        heightmap = Image.new("RGB", (width, height))
        
        for x in range(width):
            for y in range(height):
                # Read height value from the raster data
                height_value = src.read(1, window=((y, y + 1), (x, x + 1)))[0, 0]
                
                # Create an RGB color based on the height value
                color = (height_value, 0, 0)  # Red channel contains height
                
                latitude, longitude = calculate_coordinates(x, y, src.transform)
                osm_category = get_openstreetmap_category(latitude, longitude)
                category_color = get_category_color(osm_category)
                
                # Add the category color to the RGB color
                color = (color[0], category_color[1], category_color[2])
                
                # Set pixel value in heightmap image
                heightmap.putpixel((x, y), color)
    
    heightmap.save(output_image_path, "TIFF")


input_raster_path = input('input raster path')
output_image_path = input('output map path')
convert_to_heightmap(input_raster_path, output_image_path)

############################################################################################################################################################
# Step 4: Analyze Image & Create Minecraft Map (work in progress part)
level = pymclevel.MCInfdevOldLevel()
level.createFlatWorld(groundMaterial=pymclevel.alphaMaterials.Grass)

width, height = img.size
pixels = img.load()

for z in range(height):
    for x in range(width):
        pixel_color = pixels[x, z]
        feature = color_mappings.get(pixel_color, 'unknown')
        
        if feature == 'building':
            for y in range(0, 10):  # 10 blocks high
                level.setBlockAt(x, y, z, pymclevel.alphaMaterials.StoneBrick.ID)

        elif feature == 'road':
            level.setBlockAt(x, 0, z, pymclevel.alphaMaterials.Cobblestone.ID)

        elif feature == 'water':
            for y in range(0, 5):  # 5 blocks deep
                level.setBlockAt(x, y, z, pymclevel.alphaMaterials.WaterActive.ID)

        elif feature == 'green_area':
            level.setBlockAt(x, 0, z, pymclevel.alphaMaterials.Grass.ID)

        else:  # Unknown area
            for y in range(0, 5):  # Mark the unknown areas with red wool
                level.setBlockAt(x, y, z, pymclevel.alphaMaterials.RedWool.ID)


# In[ ]:


# Step 5: Save the Minecraft World
level.save('path_to_save_minecraft_world')
print("Minecraft world saved!")

