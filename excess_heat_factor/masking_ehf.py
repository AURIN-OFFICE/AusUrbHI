import netCDF4
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import shape
import geopandas as gpd

gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')
nc = netCDF4.Dataset('../_data/longpaddock_silo_lst/EHF_heatwaves____daily.nc')
data = nc.variables['EHF'][1459]

# Create a new GeoDataFrame to store the results
new_gdf = gpd.GeoDataFrame(columns=['geometry', 'max_value'], crs=gdf.crs)

# Loop over each polygon in the shapefile
for i, row in gdf.iterrows():
    # Create a mask for the current polygon
    mask = geometry_mask([shape(row['geometry'])], transform=rasterio.transform.from_origin(0, 0, 1, 1), out_shape=data.shape, invert=True)

    # Apply the mask to the netCDF data
    masked_data = np.ma.array(data, mask=mask)

    # Find the maximum value of the intersecting cells
    max_value = masked_data.max()

    # Add the result to the new GeoDataFrame
    new_gdf = new_gdf._append({'geometry': row['geometry'], 'max_value': max_value}, ignore_index=True)

# Save the new shapefile
new_gdf.to_file('../_data/longpaddock_silo_lst/new_shapefile.shp')

