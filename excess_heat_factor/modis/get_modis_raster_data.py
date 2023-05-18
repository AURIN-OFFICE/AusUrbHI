# -*- coding: utf-8 -*-
import ee
import geopandas as gpd
from shapely.geometry import Polygon

# ee.Authenticate()
ee.Initialize()


def convert_to_celsius(image):
    return image \
        .select(['LST_Day_1km', 'LST_Night_1km']) \
        .multiply(0.02) \
        .subtract(273.15)


bbox = [150.345154, -34.603824, 151.438293, -33.323644]
polygon = Polygon([(bbox[0], bbox[1]), (bbox[0], bbox[3]), (bbox[2], bbox[3]), (bbox[2], bbox[1])])

ee_geometry = ee.Geometry.Polygon(polygon.__geo_interface__["coordinates"])
start_date = "2019-12-31"
end_date = "2020-01-04"

print('getting image')
filtered_collection = ee \
    .ImageCollection("MODIS/006/MOD11A2") \
    .filterDate(start_date, end_date) \
    .filterBounds(ee_geometry) \
    .map(convert_to_celsius)
image = ee.Image(filtered_collection.first())
print('image obtained')

task = ee.batch.Export.image.toDrive(
    image=image,
    description='imageToDriveExample',
    folder='exportExample',
    scale=30,
    region=polygon
)
task.start()
