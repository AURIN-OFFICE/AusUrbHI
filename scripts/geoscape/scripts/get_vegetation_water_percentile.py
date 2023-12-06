import geopandas as gpd
import pandas as pd

# Load the shapefile
file = "../../../_data/AusUrbHI HVI data processed/Geoscape/surface_cover.shp"
gdf = gpd.read_file(file)

# Calculate quartiles for 'Trees' and 'Water' columns
# Using 'duplicates="drop"' to handle non-unique bin edges
gdf['Trees_qrt'] = pd.qcut(gdf['Trees'], q=4, duplicates='drop', labels=False)
gdf['Water_qrt'] = pd.qcut(gdf['Water'], q=4, duplicates='drop', labels=False)

# Selecting only specific columns for the CSV
columns_to_save = ['SA1_CODE21', 'Trees', 'Water', 'Trees_qrt', 'Water_qrt']
gdf_to_save = gdf[columns_to_save]

# Save to CSV
gdf_to_save.to_csv('../../_data/AusUrbHI HVI data processed/Geoscape/tree_water_quartiles.csv', index=False)
