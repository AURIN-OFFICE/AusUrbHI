import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the CSV
csv_data = pd.read_csv('GreaterSydneyLandSurfaceTemperatureLSTMODISFrom2019-12-31To2020-1-4.csv')

# Load the shapefile
shape_data = gpd.read_file('../../boundary_data/SA1_2021_AUST_GDA2020.shp')

# Ensure the SA1_CODE21 is int in both dataframes
csv_data['SA1_CODE21'] = csv_data['SA1_CODE21'].astype(str)
shape_data['SA1_CODE21'] = shape_data['SA1_CODE21'].astype(str)

# Merge the dataframes based on the SA1 codes
merged = shape_data.merge(csv_data, how='left', left_on='SA1_CODE21', right_on='SA1_CODE21')

# Fill NA values in 'mean' column after the merge (optional)
merged['mean'].fillna(0, inplace=True)

# Save the merged file as a new shapefile
merged.to_file("greater_sydney.shp")
