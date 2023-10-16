import os
import geopandas as gpd

# get all geojson file under the directory
dir_name = "C:\\Users\\haoc4\\Downloads"
file_list = os.listdir(dir_name)
geojson_files = [file for file in file_list if file.endswith('.geojson') or file.endswith('.json')]


# convert each to shapefile
for geojson_file in geojson_files:
    full_geojson_path = os.path.join(dir_name, geojson_file)
    gdf = gpd.read_file(full_geojson_path)
    shp_file_name = os.path.splitext(geojson_file)[0] + ".shp"
    full_shp_path = os.path.join(dir_name, shp_file_name)
    gdf.to_file(full_shp_path)
