import geopandas as gpd

# Read the 'sa1_nsw.shp' shapefile
sa1_nsw = gpd.read_file("sa1_nsw.shp")

# Get all unique values from the 'SA3_CODE16' column
unique_sa4_codes = sa1_nsw["SA4_CODE16"].unique()

# Read the 'SA3_2016_AUST.shp' shapefile
sa4_2016_aust = gpd.read_file("SA4_2016_AUST.shp")

# Filter the 'sa3_2016_aust' shapefile based on the unique SA3 codes from 'sa1_nsw.shp'
sa4_nsw = sa4_2016_aust[sa4_2016_aust["SA4_CODE16"].isin(unique_sa4_codes)]

# Save the refined shapefile as 'sa3_nsw.shp'
sa4_nsw.to_file("sa4_nsw.shp")