import netCDF4 as nc
import numpy as np
import xarray as xr
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import shape
import geopandas as gpd
from tqdm import tqdm
from osgeo import gdal, ogr, osr

gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')
dataset = nc.Dataset('../_data/longpaddock_silo_lst/EHF_heatwaves____daily.nc')
# 1459; 7844

# Assume that the data variable is named 'precipitation'
data = dataset.variables['EHF'][1459]

# Create a raster dataset in memory
mem_drv = gdal.GetDriverByName('MEM')
out_ds = mem_drv.Create('', data.shape[1], data.shape[0], 1, gdal.GDT_Float32)

# Write data to the raster dataset
out_band = out_ds.GetRasterBand(1)
out_band.WriteArray(data)

# Set up spatial reference system (SRS)
srs = osr.SpatialReference()
# The projection could be different depending on your data
srs.ImportFromEPSG(7844)
out_ds.SetProjection(srs.ExportToWkt())

# Convert raster to vector
mem_drv = ogr.GetDriverByName('Memory')
out_ds2 = mem_drv.CreateDataSource('out')
out_layer = out_ds2.CreateLayer('polygonized', srs=srs)
gdal.Polygonize(out_band, None, out_layer, -1, [], callback=None)

# Convert to a geopandas dataframe
geoms = []
for feature in out_layer:
    geom = feature.GetGeometryRef()
    geoms.append(geom.ExportToWkt())

gdf = gpd.GeoDataFrame(geoms, columns=['geometry'])


# Add function to check if geometry has Z coordinate
def check_3d(geom):
    # Checking if 'Z' is in the WKT string representation of the geometry
    return ' Z ' in geom


# Add a new column 'has_z' to the DataFrame
gdf['has_z'] = gdf['geometry'].apply(check_3d)


# Convert to a shapefile
gdf.to_file('../_data/longpaddock_silo_lst/new_shapefile.shp')

