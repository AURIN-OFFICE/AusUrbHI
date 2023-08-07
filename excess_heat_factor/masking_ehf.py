import netCDF4
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from tqdm import tqdm


def netcdf_to_shp(nc_file, variable, output_path):
    # Load the NetCDF file
    nc_data = netCDF4.Dataset(nc_file)
    ehf_data = nc_data.variables[variable][:]

    # Load the shapefile
    shapefile_path = '..\\_data\\study area\\ausurbhi_study_area_2021.shp'
    shapes = gpd.read_file(shapefile_path)[:10]

    # Create a list to store the maximum values
    max_values = []

    # Loop through the geometries in the shapefile
    for geometry in tqdm(shapes['geometry'], desc='Masking data', total=len(shapes)):
        # Create a mask from the geometry
        mask = geometry_mask([geometry], out_shape=ehf_data.shape[1:], transform=rasterio.Affine(1, 0, 0, 0, -1, 0),
                             invert=True)

        # Apply the mask to the EHF data
        masked_data = np.ma.array(ehf_data, mask=np.broadcast_to(mask, ehf_data.shape))

        # Find the maximum value within the geometry
        max_value = masked_data.max(axis=(1, 2)).tolist()
        max_values.append(max_value)

    # Add the maximum values to the shapefile
    shapes['max_values'] = max_values

    # Convert the maximum values to strings
    max_values_str = [','.join(map(str, values)) for values in max_values]

    # Add the maximum values to the shapefile
    shapes['max_values'] = max_values_str

    # Save the new shapefile
    shapes.to_file(output_path)


netcdf_to_shp("..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\EHF_heatwaves____daily.nc",
              "EHF", "..\\_data\\AusUrbHI HVI data processed\\Longpaddock SILO LST\\ehf.shp")
