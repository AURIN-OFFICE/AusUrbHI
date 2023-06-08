import geopandas as gpd
import pandas as pd

# transform ABS data by region persons born overseas 2021 csv to shapefile
csv = pd.read_csv(r'..\..\_data\data_by_region_persons_born_overseas_asgs_name_modified.csv')
shp = gpd.read_file(r'..\..\_data\boundary_data\SA2_2021_AUST_GDA2020.shp')
shp = shp[['SA2_CODE21', 'geometry']]

csv['year'] = csv['year'].astype(str)
shp['SA2_CODE21'] = shp['SA2_CODE21'].astype(str)

# Select rows with 'Year' equal to 2021 (string or integer)
csv = csv[csv['year'].astype(str) == '2021']

# Rename 'Code' column in csv to 'SA2_CODE21' for merge operation
csv = csv.rename(columns={'code': 'SA2_CODE21'})

# Merge the shapefile and csv data
merged = pd.merge(csv, shp, on='SA2_CODE21', how='inner')
merged = gpd.GeoDataFrame(merged, geometry='geometry')
merged.to_file(r'..\..\_data\AusUrbHI HVI data\other ABS datasets'
               r'\abs_data_by_region_persons_born_overseas_asgs_sa2_2021.geojson', driver='GeoJSON')
