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

# Prepare a dictionary to hold our density data
density_data = {f"{key}_den": [] for key in service_gdfs}

# Calculate densities
for key, service_gdf in service_gdfs.items():
    for sa1_row in tqdm(study_area_gdf.itertuples(index=False),
                        total=study_area_gdf.shape[0],
                        desc=f"Calculating {key} density"):
        # Count the number of intersecting polygons
        intersections = service_gdf.geometry.intersects(sa1_row.geometry)
        count_intersections = intersections.sum()

        # Calculate the density (number of polygons per square km of SA1 area)
        density = round(count_intersections / sa1_row.AREASQKM21, 2)
        density_data[f"{key}_den"].append(density)

# Add density data to the study area GeoDataFrame
for key, values in density_data.items():
    study_area_gdf[key] = values

# Keep only the specified fields
fields_to_keep = ['SA1_CODE21', 'geometry'] + list(density_data.keys())
study_area_gdf = study_area_gdf[fields_to_keep]

# Save the modified study area GeoDataFrame as a new shapefile
output_path = "../_data/AusUrbHI HVI data processed/NHSD/gp_ed_within_network_threshold.shp"
study_area_gdf.to_file(output_path)
