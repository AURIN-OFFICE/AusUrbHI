import xarray as xr
import geopandas as gpd
import json
from shapely.geometry import mapping
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_row(i, row, nc_file, shapefile):
    # Clip the NetCDF file by the current polygon
    clipped_nc = nc_file.rio.clip([mapping(row.geometry)], shapefile.crs, all_touched=True)

    # Convert the clipped NetCDF file to a dataframe, with maximum value only rather than all values
    clipped_df = clipped_nc.to_dataframe().reset_index().groupby(['time']).max().reset_index()

    result = {}
    # For each column other than "time", "lat", and "lon", create a list of the maximum values, convert to string
    # and join with a comma, then add to the output shapefile
    for column in clipped_df.columns:
        if column not in ["time", "lat", "lon", "spatial_ref"]:
            value_list = clipped_df[column].astype(str).tolist()

            # For each year, create a field in the output shapefile of the corresponding column values
            for year in [2016, 2017, 2018, 2019, 2020, 2021]:
                start, end = year_to_indices(year)
                value_list_year = value_list[start:end]
                if "end" not in column:
                    value_dict = {k: round(float(v), 1) for k, v in enumerate(value_list_year)
                                  if v != "0 days" and v != "0.0" and v != "0"}
                else:
                    value_dict = {k: v for k, v in enumerate(value_list_year)
                                  if v != "0 days" and v != "0.0" and v != "0"}
                value = json.dumps(value_dict)

                # Split data into multiple columns if it is too long
                if value != "{}" and len(value) > 0:
                    chunks = [value[i:i + 254] for i in range(0, len(value), 254)]
                    for idx, chunk in enumerate(chunks, 1):
                        suffix = str(year)[-2:] if idx == 1 else f"{str(year)[-2:]}_{idx}"
                        result[f"{column}{suffix}"] = chunk
    return i, result


def year_to_indices(year):
    """convert a year from 2016 to 2021 into start and ending index from the netcdf value list"""
    year_start = (year - 2015) * 365
    year_end = year_start + 365
    return year_start, year_end

# Open the NetCDF file
nc_file = xr.open_dataset("..\\_data\\AusUrbHI HVI data unprocessed\\Longpaddock SILO LST\\"
                          "merged_heatwaves.nc")
nc_file = nc_file.rio.write_crs("EPSG:7844", inplace=True)

# Open the shapefile
shapefile = gpd.read_file('..\\_data\\study area\\ausurbhi_study_area_2016_with_pha.shp')

# Create a copy of the shapefile to modify
output_shapefile = shapefile[['SA1_MAIN16', 'geometry']].copy()

# Create a ThreadPoolExecutor
with ThreadPoolExecutor() as executor:
    # Submit the tasks to the executor
    futures = [executor.submit(process_row, i, row, nc_file, shapefile) for i, row in shapefile.iterrows()]

    # Collect the results
    for future in tqdm(as_completed(futures), total=len(shapefile), desc="Clipping polygons"):
        i, result = future.result()
        for key, value in result.items():
            output_shapefile.loc[i, key] = value

# Save the shapefile
output_shapefile.to_file(f"..\\_data\\AusUrbHI HVI data processed\\Longpaddock SILO LST\\merged_heatwaves.shp")
