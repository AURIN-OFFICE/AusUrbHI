import geopandas as gpd
import xarray as xr
from shapely.geometry import mapping

# read the shapefile from ../_data/study area/ausurbhi_study_area_2021.shp, and
# netcdf from ./_data/longpaddock_silo_lst/max/2016_2021_max_temp.nc. Refine the
# netcdf so it only contains raster cells that intersects with all the defined
# SA1 regions from the shapefile.

shapefile = gpd.read_file('..\\_data\\study area\\ausurbhi_study_area_2021.shp', crs="epsg:7844")
for m in ('max', 'min'):
    netcdf = xr.open_dataset(f'..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\'
                             f'{m}\\2015_2022_{m}_temp.nc')
    netcdf.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    netcdf = netcdf.rio.write_crs("EPSG:7844", inplace=True)

    # unbuffered version
    clipped = netcdf.rio.clip(shapefile.geometry.apply(mapping), shapefile.crs)
    clipped.to_netcdf(f'..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\'
                      f'2015_2022_{m}_temp_clipped_unbuffered.nc')

    # buffered version
    shapefile_buffered = shapefile.buffer(0.05)
    clipped = netcdf.rio.clip(shapefile_buffered.geometry.apply(mapping), shapefile.crs)
    clipped.to_netcdf(f'..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\'
                      f'2015_2022_{m}_temp_clipped_buffered.nc')