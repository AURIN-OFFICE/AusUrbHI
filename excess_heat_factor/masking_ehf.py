import geopandas as gpd
import xarray as xr
import pandas as pd

# Read the input shapefile
input_shapefile = '..\\_data\\study area\\ausurbhi_study_area_2021.shp'
gdf = gpd.read_file(input_shapefile, crs="epsg:7844")

# Open the NetCDF file
nc_file = "..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\EHF_heatwaves____daily.nc"
netcdf = xr.open_dataset(nc_file)
netcdf.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
netcdf = netcdf.rio.write_crs("EPSG:7844", inplace=True)

# Create a DataFrame to store the results
result_df = pd.DataFrame(columns=['SA1_CODE21', 'values'])

# Iterate through the geometries in the shapefile
for index, row in gdf.iterrows():
    # Clip the NetCDF file using the geometry
    clipped_ds = netcdf.rio.clip([row['geometry']])

    # Extract the maximum value for each day and store in a list
    max_values = clipped_ds.max(dim=['x', 'y']).to_dataframe().values.tolist()[365:-365]

    # Append the results to the DataFrame
    result_df = result_df.append({'SA1_CODE21': row['SA1_CODE21'], 'values': str(max_values)}, ignore_index=True)

# Merge the results with the original GeoDataFrame
gdf_result = gdf.merge(result_df, on='SA1_CODE21')

# Write the new shapefile
output_shapefile = "..\\_data\\AusUrbHI HVI data processed\\Longpaddock SILO LST\\ehf.shp"
gdf_result.to_file(output_shapefile)
