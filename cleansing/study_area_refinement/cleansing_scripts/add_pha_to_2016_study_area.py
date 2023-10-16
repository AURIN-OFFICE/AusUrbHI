import pandas as pd
import geopandas as gpd
from collections import defaultdict

# Read the CSV file
csv_path = "..\\..\\_data\\study area\\PHIDU_2016_SA2_PHA.csv"
df = pd.read_csv(csv_path)

# Convert the "SA2 code" and "PHA code" columns to strings
df['SA2 code'] = df['SA2 code'].astype(str)
df['PHA code'] = df['PHA code'].astype(str)

# Check if the mapping is n:1
mapping = defaultdict(set)
for index, row in df.iterrows():
    sa2_code = row['SA2 code']
    pha_code = row['PHA code']
    mapping[pha_code].add(sa2_code)

n_to_one_mapping = True
for pha_code, sa2_codes in mapping.items():
    if len(sa2_codes) < 1:
        print(f"PHA code {pha_code} has no corresponding SA2 codes.")
        n_to_one_mapping = False
        break

if n_to_one_mapping:
    print("The mapping is n:1.")
else:
    print("The mapping is not n:1.")
    exit()

# Read the shapefile
shapefile_path = "..\\..\\_data\\study area\\sa1_nsw.shp"
gdf = gpd.read_file(shapefile_path)

# Create a dictionary for mapping SA2 code to PHA code
sa2_to_pha_mapping = {str(row['SA2 code']): str(row['PHA code']) for index, row in df.iterrows()}

# Convert the "SA2_MAIN16" field to string
gdf['SA2_MAIN16'] = gdf['SA2_MAIN16'].astype(str)

# Add a new field "pha_code" to the shapefile
gdf['pha_code'] = gdf['SA2_MAIN16'].map(sa2_to_pha_mapping)

# Save the updated shapefile
gdf.to_file("..\\..\\_data\\study area\\ausurbhi_study_area_2016_with_pha.shp")
