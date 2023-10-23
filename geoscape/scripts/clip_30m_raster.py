from osgeo import gdal, ogr

# Paths
raster_one_path = ("../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/surface_tif_raw/"
                   "ACTNSW_SURFACECOVER_30M_Z55.tif")
raster_two_path = ("../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/surface_tif_raw/"
                   "NSW_SURFACECOVER_30M_Z56.tif")
study_area_shapefile_path = "../../_data/study area/ausurbhi_study_area_2021.shp"

# Create a buffer around the shapefile
driver = ogr.GetDriverByName("ESRI Shapefile")
dataSource = driver.Open(study_area_shapefile_path, 1)  # 1 means with write access
layer = dataSource.GetLayer()
for feature in layer:
    geom = feature.GetGeometryRef()
    geom_buffer = geom.Buffer(30)  # 30m buffer
    feature.SetGeometry(geom_buffer)
    layer.SetFeature(feature)
dataSource = None  # Save and close the shapefile


# Function to clip and save raster
def clip_raster_with_shapefile(raster_path, shape_path, output_path):
    options = gdal.WarpOptions(cutlineDSName=shape_path, cropToCutline=True)
    gdal.Warp(output_path, raster_path, options=options)


# Clip the rasters
output_folder = "../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/surface_tif_clipped"
clip_raster_with_shapefile(raster_one_path, study_area_shapefile_path, output_folder + "clipped_z55.tif")
clip_raster_with_shapefile(raster_two_path, study_area_shapefile_path, output_folder + "clipped_z56.tif")
