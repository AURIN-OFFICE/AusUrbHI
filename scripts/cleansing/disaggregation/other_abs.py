import os
import geopandas as gpd
from tqdm import tqdm
from disaggregation_mapper import DisaggregationMapper

folder_path = "../../../_data/AusUrbHI HVI data processed/other ABS datasets by 2021 concordance"
study_area_gdf = gpd.read_file("../../_data/study area/ausurbhi_study_area_2021.shp")
output_folder_path = "../../../_data/AusUrbHI HVI data processed"

mapper = DisaggregationMapper()

for filename in tqdm(os.listdir(folder_path),
                     total=len(os.listdir(folder_path)), desc="Disaggregating other ABS datasets"):
    mapper.filename = filename

    if filename.endswith(".shp"):
        file_path = os.path.join(folder_path, filename)
        gdf = gpd.read_file(file_path)

        if "sa2" in filename:
            # first, convert shapefile to SA1 level
            gdf = mapper.convert_sa2_gdf_to_sa1(gdf, study_area_gdf)

            # second, for each division method, divide and save shapefile
            exclude_division_field_list = ['SA1_CODE21', 'SA2_CODE21', 'Shape', 'id', 'sa2_name_2', 'yr',
                                           'SA2_MAIN16', 'state_code', 'state_name', 'sa2_code5d', 'sa2_name16',
                                           'gccsa_code', 'gccsa_name', 'sa4_code16', 'sa4_name16', 'sa3_code16',
                                           'sa3_name16', 'sa2_name16', 'geometry', 'index', 'STATE_CODE',
                                           'STATE_NAME', 'GCCSA_CODE', 'GCCSA_NAME', 'SA4_CODE_2', 'SA4_NAME_2',
                                           'SA3_CODE_2', 'SA3_NAME_2', 'SA2_CODE_2', 'SA2_NAME_2', 'label', 'year',
                                           'INDIV_QLTY', 'OVR_QLTY', 'RATIO']
            equal_divided_gdf = mapper.divide_field_values(gdf, exclude_division_field_list, "SA2", "equal")
            population_divided_gdf = mapper.divide_field_values(gdf, exclude_division_field_list, "SA2", "population")

        else:
            equal_divided_gdf = gdf.copy()
            population_divided_gdf = gdf.copy()
        no_divided_gdf = gdf.copy()

        # save the file
        for string in ["equal_divide", "population_divide", "no_divide"]:
            output_filename = f'other ABS datasets by 2021 and sa1 concordance {string.replace("_", " ")}/' + \
                              filename.replace('_2021_concordance.shp', f'_2021_sa1_concordance_{string}.shp')
            output_path = os.path.join(output_folder_path, output_filename)
            if string == "equal_divide":
                equal_divided_gdf.to_file(output_path)
            elif string == "population_divide":
                population_divided_gdf.to_file(output_path)
            else:
                no_divided_gdf.to_file(output_path)
