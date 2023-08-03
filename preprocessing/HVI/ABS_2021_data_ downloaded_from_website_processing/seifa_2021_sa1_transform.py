import geopandas as gpd
import pandas as pd

# transform seifa 2021 csv to shapefile
csv = pd.read_csv(r'..\..\_data\seifa_irsad_2021_sa1.csv')
shp = gpd.read_file(r'..\..\_data\boundary_data\SA1_2021_AUST_GDA2020.shp')
shp = shp[['SA1_CODE21', 'geometry']]

csv['SA1_CODE21'] = csv['SA1_CODE21'].astype(str)
shp['SA1_CODE21'] = shp['SA1_CODE21'].astype(str)

merged = pd.merge(csv, shp, on='SA1_CODE21', how='inner')
merged = gpd.GeoDataFrame(merged, geometry='geometry')
merged.to_file(r'..\..\_data\AusUrbHI HVI data\other ABS cleansing_scripts\seifa_irsad_aust_sa1_2021.shp')
