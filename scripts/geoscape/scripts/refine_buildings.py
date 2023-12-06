import geopandas as gpd
from shapely.geometry import Point

# Load only necessary columns
cols_meshblock = ['MB_CODE21', 'SA1_CODE21']
meshblock_gdf = gpd.read_file("../../_data/study area/meshblock_study_area_2021.shp",
                              usecols=cols_meshblock,
                              ignore_geometry=True)
cols_buildings = ['MB_CODE', 'SP_ADJ', 'ROOF_HGT', 'PR_RF_MA', 'AREA', 'EST_LEV']
buildings_gdf = gpd.read_file("../../_data/AusUrbHI HVI data unprocessed/Geoscape/"
                              "Buildings_JUN23_NSW_GDA94_SHP_317/Buildings/Buildings JUNE 2023/"
                              "Standard/nsw_buildings.shp",
                              usecols=cols_buildings,
                              ignore_geometry=True)
print("data loaded.")

# refine entries to study area using set intersection
study_area_meshblock_codes = set(meshblock_gdf['MB_CODE21'])
buildings_gdf = buildings_gdf[buildings_gdf['MB_CODE'].isin(study_area_meshblock_codes)]
print("refined buildings data to study area.")

# Add SA1 code as field to building datasd
meshblock_sa1_code_dict = meshblock_gdf.set_index('MB_CODE21')['SA1_CODE21'].to_dict()
buildings_gdf['SA1_CODE21'] = buildings_gdf['MB_CODE'].map(meshblock_sa1_code_dict)
print("added SA1 code to buildings data.")

# Convert to GeoDataFrame with dummy geometry
geometry = [Point(0, 0) for _ in range(len(buildings_gdf))]
buildings_gdf = gpd.GeoDataFrame(buildings_gdf, geometry=geometry)
print("geometry added.")

# Save
output_path = "../../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/buildings_in_study_area.shp"
buildings_gdf.to_file(output_path)
print("saved to", output_path)
