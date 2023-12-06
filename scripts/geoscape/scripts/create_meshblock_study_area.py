import geopandas as gpd

# Load the shapefiles
meshblock_gdf = gpd.read_file("../../_data/study area/MB_2021_AUST_GDA2020.shp")
study_area_gdf = gpd.read_file("../../_data/study area/ausurbhi_study_area_2021.shp")

# Extract the SA1_CODE21 values from the study area shapefile
study_area_sa1_codes = set(study_area_gdf['SA1_CODE21'])

# Filter the meshblock dataframe to only include rows with SA1_CODE21 values that exist in the study area
filtered_meshblock_gdf = meshblock_gdf[meshblock_gdf['SA1_CODE21'].isin(study_area_sa1_codes)]

# Save the filtered dataframe to a new shapefile
output_path = "../../../_data/study area/meshblock_study_area_2021.shp"
filtered_meshblock_gdf.to_file(output_path)
