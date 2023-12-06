import geopandas as gpd
from tqdm import tqdm

input_file = "../../_data/AusUrbHI HVI data unprocessed/NHSD/nhsd_nov2020_utf8.shp"
# note, the study area file is already buffered by 800/2000m/5000m using arcgis pro
study_area_file_800 = "../../_data/AusUrbHI HVI data unprocessed/NHSD/ausurbhi_study_area_2021.shp"
study_area_file_2000 = "../../_data/AusUrbHI HVI data unprocessed/NHSD/ausurbhi_study_area_2021_2000m_buffer.shp"
study_area_file_5000 = "../../_data/AusUrbHI HVI data unprocessed/NHSD/ausurbhi_study_area_2021_5000m_buffer.shp"
output_file = "../../_data/AusUrbHI HVI data processed/NHSD/gp_ed_within_threshold.shp"

nhsd_df = gpd.read_file(input_file)
study_area_df_800 = gpd.read_file(study_area_file_800)
study_area_df_2000 = gpd.read_file(study_area_file_2000)
study_area_df_5000 = gpd.read_file(study_area_file_5000)

# create sa1 area dict
sa1_area_dict = study_area_df_800.set_index('SA1_CODE21')['AREASQKM21'].to_dict()

# Create a new DataFrame for output
new_df = study_area_df_800[['SA1_CODE21', 'geometry', 'AREASQKM21']].copy()

# Ensure both are in the GDA94 CRS
gda94_crs = 'EPSG:4283'
if nhsd_df.crs != gda94_crs:
    nhsd_df = nhsd_df.to_crs(gda94_crs)
for df in [study_area_df_800, study_area_df_2000, study_area_df_5000]:
    if df.crs != gda94_crs:
        df = df.to_crs(gda94_crs)

# Count the points within the buffer
gp_counts = []
ed_counts = []

for area in tqdm(study_area_df_800.geometry,
                 desc=f"Counting services within 800m buffer",
                 total=len(study_area_df_800)):
    gp_count = nhsd_df[nhsd_df['snomed_nm'] == 'General practice service'].within(area).sum()
    gp_counts.append(gp_count)

    ed_count = nhsd_df[nhsd_df['snomed_nm'] == 'Emergency department service'].within(area).sum()
    ed_counts.append(ed_count)

new_df['gp_in_800m'] = gp_counts
new_df['ed_in_800m'] = ed_counts
new_df['gp_density'] = new_df['gp_in_800m'] / new_df['AREASQKM21']
new_df['ed_density'] = new_df['ed_in_800m'] / new_df['AREASQKM21']

print(new_df.head())

# Count the points within the buffer
gp_counts = []
ed_counts = []

for area in tqdm(study_area_df_2000.geometry,
                 desc=f"Counting services within 2000m buffer",
                 total=len(study_area_df_2000)):
    gp_count = nhsd_df[nhsd_df['snomed_nm'] == 'General practice service'].within(area).sum()
    gp_counts.append(gp_count)

    ed_count = nhsd_df[nhsd_df['snomed_nm'] == 'Emergency department service'].within(area).sum()
    ed_counts.append(ed_count)

new_df['gp_in_2km'] = gp_counts
new_df['ed_in_2km'] = ed_counts
new_df['gp_2km_den'] = new_df['gp_in_2km'] / new_df['AREASQKM21']
new_df['ed_2km_den'] = new_df['ed_in_2km'] / new_df['AREASQKM21']

print(new_df.head())

# Count the points within the buffer
gp_counts = []
ed_counts = []

for area in tqdm(study_area_df_5000.geometry,
                 desc=f"Counting services within 5000m buffer",
                 total=len(study_area_df_5000)):
    gp_count = nhsd_df[nhsd_df['snomed_nm'] == 'General practice service'].within(area).sum()
    gp_counts.append(gp_count)

    ed_count = nhsd_df[nhsd_df['snomed_nm'] == 'Emergency department service'].within(area).sum()
    ed_counts.append(ed_count)

new_df['gp_in_5km'] = gp_counts
new_df['ed_in_5km'] = ed_counts
new_df['gp_5km_den'] = new_df['gp_in_5km'] / new_df['AREASQKM21']
new_df['ed_5km_den'] = new_df['ed_in_5km'] / new_df['AREASQKM21']

print(new_df.head())

# Restoring the original geometry for SA1 areas (without the buffer)
study_area_df = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')
new_df['geometry'] = study_area_df['geometry']

new_df.to_file(output_file)