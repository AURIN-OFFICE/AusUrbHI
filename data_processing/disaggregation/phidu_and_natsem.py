import os
import geopandas as gpd
from concordance_mapper import ConcordanceMapper

folder_path = "../_data/AusUrbHI HVI data processed/PHIDU and NATSEM datasets by 2021 concordance"
study_area_shp_path = "../_data/study area/ausurbhi_study_area_2021.shp"
study_area_gdf = gpd.read_file(study_area_shp_path)
output_folder_path = "../_data/AusUrbHI HVI data processed/PHIDU and NATSEM datasets by 2021 and sa1 concordance"

mapper = ConcordanceMapper()

# create a dictionary of pha codes and number of SA2s in each pha
pha_has_number_of_sa2_dict = mapper.create_pha_has_number_of_sa2_dict()

# create a dictionary of sa2 codes and number of SA1s in each sa2
sa2_has_number_of_sa1_dict = mapper.create_sa2_has_number_of_sa1_dict()

for filename in os.listdir(folder_path):
    mapper.filename = filename

    if filename.endswith(".shp"):
        file_path = os.path.join(folder_path, filename)
        gdf = gpd.read_file(file_path)

        if "phidu" in filename:
            exclude_division_field_list = ['Shape', 'id', 'fid', 'pha_code', 'pha_name', 'SA2_CODE21', 'geometry']

            # divide PHIDU data value by number of SA2s in PHA
            pha_2_sa2_gdf = mapper.divide_pha_data_by_number_of_sa2(gdf, exclude_division_field_list)

            # save the temporary file for reference purpose
            temp_output_filename = filename.replace('_2021_concordance.shp', '_2021_pha_concordance.shp')
            temp_folder = "../_data/AusUrbHI HVI data processed/PHIDU and NATSEM datasets by 2021 and pha concordance"
            temp_output_path = os.path.join(temp_folder, temp_output_filename)
            pha_2_sa2_gdf.to_file(temp_output_path)

            # convert SA2 shp to SA1 shp and divide SA2 data value by number of SA1s in SA2
            result_gdf = mapper.convert_sa2_to_sa1_and_divide(pha_2_sa2_gdf, study_area_gdf,
                                                              exclude_division_field_list)

        else:
            exclude_division_field_list = ['Shape', 'id', 'SA2_CODE21', 'sa2_name16', 'geometry']

            # convert sa2 shp to sa1 shp and divide sa2 data value by number of sa1s in sa2
            result_gdf = mapper.convert_sa2_to_sa1_and_divide(gdf, study_area_gdf,
                                                              exclude_division_field_list)

        # save the file
        result_gdf = mapper.cleanse_geometry(result_gdf, study_area_gdf)
        output_filename = filename.replace('_2021_concordance.shp', '_2021_sa1_concordance.shp')
        output_path = os.path.join(output_folder_path, output_filename)
        result_gdf.to_file(output_path)
