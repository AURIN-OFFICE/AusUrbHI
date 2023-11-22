import geopandas as gpd
from tqdm import tqdm

# Load the study area shapefile
study_area_path = "../_data/study area/ausurbhi_study_area_2021.shp"
study_area_gdf = gpd.read_file(study_area_path)

# Paths for the service area shapefiles (assuming a common base path)
base_path = "../_data/AusUrbHI HVI data unprocessed/NHSD/service analysis result"
service_files = {
    "gp_1km": f"{base_path}/gp_polygons_1000.shp",
    "gp_2km": f"{base_path}/gp_polygons_2000.shp",
    "gp_5km": f"{base_path}/gp_polygons_5000.shp",
    "ed_1km": f"{base_path}/ed_polygons_1000.shp",
    "ed_2km": f"{base_path}/ed_polygons_2000.shp",
    "ed_5km": f"{base_path}/ed_polygons_5000.shp",
}

# Load service area shapefiles
service_gdfs = {key: gpd.read_file(path) for key, path in service_files.items()}

# Calculate densities and add new fields to the study area GeoDataFrame
for key in service_gdfs:
    # Initialize the new field with zeros
    study_area_gdf[f"{key}_den"] = 0.0
    for index, sa1_row in tqdm(study_area_gdf.iterrows(),
                               total=len(study_area_gdf),
                               desc=f"Calculating {key} density"):
        # Count the number of intersecting polygons
        intersections = service_gdfs[key].geometry.intersects(sa1_row.geometry)
        count_intersections = intersections.sum()

        # Calculate the density (number of polygons per square km of SA1 area)
        density = count_intersections / sa1_row['AREASQKM21']
        study_area_gdf.at[index, f"{key}_den"] = density

# Save the modified study area GeoDataFrame as a new shapefile
output_path = r"..\_data\AusUrbHI HVI data processed\NHSD\gp_ed_within_network_threshold.shp"
study_area_gdf.to_file(output_path)