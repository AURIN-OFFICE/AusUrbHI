import geopandas as gpd

meshblock_gdf = gpd.read_file("../../_data/study area/meshblock_study_area_2021.shp")
buildings_gdf = gpd.read_file("../../_data/AusUrbHI HVI data unprocessed/Geospace/Buildings_JUN23_NSW_GDA94_SHP_317/"
                              "Buildings/Buildings JUNE 2023/Standard/nsw_buildings.shp")

study_area_meshblock_codes = set(meshblock_gdf['MB_CODE21'])
filtered_meshblock_gdf = buildings_gdf[buildings_gdf['MB_CODE'].isin(study_area_meshblock_codes)]

output_path = "../../_data/AusUrbHI HVI data processed/Geoscape/temporary/buildings_in_study_area.shp"
filtered_meshblock_gdf.to_file(output_path)
