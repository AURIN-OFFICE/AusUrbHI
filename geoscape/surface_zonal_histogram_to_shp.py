import pandas as pd
import geopandas as gpd
import os

# Step 1: Read the Excel file and drop the first column
df = pd.read_excel("../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/surface/surface_histogram/surface_histogram.xlsx")
df.drop(columns=['Rowid'], inplace=True)

# Step 2: Modify the LABEL column values
df['LABEL'] = df['LABEL'].str.extract(r'(\d+)$')[0]

# Step 3: Read the study area shapefile and merge
gdf_study_area = gpd.read_file("../_data/study area/ausurbhi_study_area_2021.shp")
merged_gdf = gdf_study_area[['geometry', 'SA1_CODE21']].merge(df, left_on='SA1_CODE21', right_on='LABEL', how='right')

# Drop the duplicate SA1_CODE21 column
merged_gdf.drop(columns=['LABEL'], inplace=True)

# Step 4: Delete columns that only have 0 values
cols_to_drop = [col for col in merged_gdf.columns if (merged_gdf[col] == 0).all()]
merged_gdf.drop(columns=cols_to_drop, inplace=True)
merged_gdf.crs = gdf_study_area.crs

# Step 5: Calculate the sum for each row (excluding the geometry and SA1_CODE21 columns)
merged_gdf['total_landuse_cells'] = merged_gdf.drop(columns=['geometry', 'SA1_CODE21']).sum(axis=1)

# Step 6: Calculate the proportion for each land use type column and round to two decimal places
landuse_columns = merged_gdf.columns.difference(['geometry', 'SA1_CODE21', 'total_landuse_cells'])

for column in landuse_columns:
    merged_gdf[column] = (merged_gdf[column] / merged_gdf['total_landuse_cells']).round(2)

# Step 7: Ensure directory exists before saving
output_dir = "../_data/AusUrbHI HVI data processed/Geoscape"
output_path = os.path.join(output_dir, "surface.shp")
merged_gdf.to_file(output_path)

print("Shapefile saved successfully!")
