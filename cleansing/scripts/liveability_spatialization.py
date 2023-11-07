import geopandas as gpd
import pandas as pd

# Read the csv and shapefile data
csv_data = pd.read_csv(r'../../_data/AusUrbHI HVI data unprocessed/Liveability/LiveabilityIndex_sydney_2021_sa1.csv')
shp_data = gpd.read_file(r'../../_data/study area/ausurbhi_study_area_2021.shp')

# Convert the merge columns to string type
csv_data['sa1'] = csv_data['sa1'].astype(str)
shp_data['SA1_CODE21'] = shp_data['SA1_CODE21'].astype(str)

# Merge the csv data with the shapefile based on the 'sa1' and 'SA1_CODE21' fields
merged_data = shp_data.merge(csv_data, left_on='SA1_CODE21', right_on='sa1')

# Save the merged data to a new shapefile
output_path = r'../../_data/AusUrbHI HVI data processed/Liveability/LiveabilityIndex_sydney_2021_sa1.shp'
merged_data.to_file(output_path)
