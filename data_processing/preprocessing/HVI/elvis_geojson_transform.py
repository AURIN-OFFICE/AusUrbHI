import geopandas as gpd

# gdf = gpd.read_file("../../_data/boundary_data/boundaries.shp")
# gdf.to_file("../../_data/boundary_data/boundaries.json", driver="GeoJSON")

import json

# read json file
data = json.load(open('../../_data/boundary_data/boundaries.json'))
print(len(data["features"][0]["geometry"]["coordinates"]))


