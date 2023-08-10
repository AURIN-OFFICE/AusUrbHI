import xarray as xr
import geopandas as gpd
from shapely.geometry import mapping
from tqdm import tqdm

# Open the NetCDF file
nc_file = xr.open_dataset(
    "..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\EHF_heatwaves____daily_filled.nc")
nc_file = nc_file.rio.write_crs("EPSG:7844", inplace=True)

# Open the shapefile
shapefile = gpd.read_file('..\\_data\\study area\\ausurbhi_study_area_2021.shp')

# Loop through each polygon in the shapefile
for i, row in tqdm(shapefile.iterrows(), total=len(shapefile), desc="Clipping polygons"):
    # Clip the NetCDF file by the current polygon
    clipped_nc = nc_file.rio.clip([mapping(row.geometry)], shapefile.crs, all_touched=True)

    # Save the clipped NetCDF file
    pass
