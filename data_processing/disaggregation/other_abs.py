import os
import json
import geopandas as gpd
from disaggregation_mapper import DisaggregationMapper

folder_path = "../_data/AusUrbHI HVI data processed/other ABS datasets by 2021 concordance"
study_area_gdf = gpd.read_file("../_data/study area/ausurbhi_study_area_2021.shp")
output_folder_path = "../_data/AusUrbHI HVI data processed/other ABS datasets by 2021 and sa1 concordance"

with open('population_dicts.json', 'r') as f:
    sa1_population_ratio_in_sa2_dict, sa2_population_ratio_in_pha_dict = json.load(f)
mapper = DisaggregationMapper()

# create a dictionary of sa2 codes and number of SA1s in each sa2
sa2_has_number_of_sa1_dict = mapper.create_sa2_has_number_of_sa1_dict()

for filename in os.listdir(folder_path):
    mapper.filename = filename

    if filename.endswith(".shp"):
        file_path = os.path.join(folder_path, filename)
        gdf = gpd.read_file(file_path)

        if "sa2" in filename:
            exclude_division_field_list = ['Shape', 'id', 'sa2_name_2', 'yr', 'SA2_MAIN16',
                                           'state_code', 'state_name', 'sa2_code5d', 'sa2_name16',
                                           'gccsa_code', 'gccsa_name', 'sa4_code16', 'sa4_name16',
                                           'sa3_code16', 'sa3_name16', 'sa2_name16', 'geometry',
                                           'index', 'STATE_CODE', 'STATE_NAME', 'GCCSA_CODE',
                                           'GCCSA_NAME', 'SA4_CODE_2', 'SA4_NAME_2', 'SA3_CODE_2',
                                           'SA3_NAME_2', 'SA2_CODE_2', 'SA2_NAME_2', 'label', 'year']

            # convert SA2 shp to SA1 shp and divide SA2 data value by number of SA1s in SA2
            result_gdf = mapper.convert_sa2_to_sa1_and_divide(gdf, study_area_gdf,
                                                              exclude_division_field_list)

        else:
            result_gdf = gdf.copy()

        # save the file
        result_gdf = mapper.cleanse_geometry(result_gdf, study_area_gdf)
        output_filename = filename.replace('_2021_concordance.shp', '_2021_sa1_concordance.shp')
        output_path = os.path.join(output_folder_path, output_filename)
        result_gdf.to_file(output_path)
