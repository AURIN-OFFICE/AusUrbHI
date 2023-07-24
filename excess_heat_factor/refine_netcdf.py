import geopandas as gpd
import xarray as xr
import rioxarray
from shapely.geometry import mapping

# read the shapefile from ../_data/study area/ausurbhi_study_area_2021.shp, and
# netcdf from ./_data/longpaddock_silo_lst/max/2016_2021_max_temp.nc. Refine the
# netcdf so it only contains raster cells that intersects with all the defined
# SA1 regions from the shapefile.

shapefile = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')
netcdf = xr.open_dataset('../_data/longpaddock_silo_lst/max/2016.max_temp.nc')
netcdf = netcdf.rio.write_crs("EPSG:4326")

clipped = []
for _, row in shapefile.iterrows():
    clipped.append(netcdf.rio.clip([row['geometry']]))
clipped_netcdf = xr.concat(clipped, dim='SA1')

clipped_netcdf.to_netcdf('../_data/longpaddock_silo_lst/max/clipped_2016_2021_max_temp.nc')
