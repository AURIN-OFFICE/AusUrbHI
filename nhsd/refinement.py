import geopandas as gpd
from tqdm import tqdm

input_file = "../_data/AusUrbHI HVI data unprocessed/NHSD/nhsd_nov2020_utf8.shp"
study_area_file = "../_data/study area/ausurbhi_study_area_2021.shp"
output_file = "../_data/AusUrbHI HVI data processed/NHSD/gp_ed_within_800m.shp"

nhsd_df = gpd.read_file(input_file)
study_area_df = gpd.read_file(study_area_file)

# Create a new DataFrame for output
new_df = study_area_df[['SA1_CODE21', 'geometry']].copy()

# Ensure both are in the GDA94 CRS
gda94_crs = 'EPSG:4283'
if nhsd_df.crs != gda94_crs:
    nhsd_df = nhsd_df.to_crs(gda94_crs)
if study_area_df.crs != gda94_crs:
    study_area_df = study_area_df.to_crs(gda94_crs)

# Buffer the study areas by 800m
study_area_df['geometry'] = study_area_df.buffer(800)


# Count the points within the buffer
def count_services(service_name, buffered_areas, points):
    counts = []
    for area in tqdm(buffered_areas.geometry,
                     desc=f"Counting {service_name} services",
                     total=len(buffered_areas)):
        count = points[points['snomed_nm'] == service_name].within(area).sum()
        counts.append(count)
    return counts


new_df['gp_count'] = count_services('General practice service', study_area_df, nhsd_df)
new_df['ed_count'] = count_services('Emergency department service', study_area_df, nhsd_df)
new_df.to_file(output_file)
