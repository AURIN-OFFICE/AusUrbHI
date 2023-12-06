import os
import pandas as pd
import geopandas as gpd
from scripts.concordance_mapper import ConcordanceMapper

sa1_csv_path = "../../../_data/study area/CG_SA1_2016_SA1_2021.csv"
sa1_csv_df = pd.read_csv(sa1_csv_path)

sa2_csv_path = "../../../_data/study area/CG_SA2_2016_SA2_2021.csv"
sa2_csv_df = pd.read_csv(sa2_csv_path)

study_area_path = "../../../_data/study area/ausurbhi_study_area_2021.shp"
study_area_df = gpd.read_file(study_area_path)

folder_path = "../../../_data/AusUrbHI HVI data processed/other ABS datasets"
output_folder_path = "../../../_data/AusUrbHI HVI data processed/other ABS datasets by 2021 concordance"

for filename in os.listdir(folder_path):
    if filename.endswith(".shp"):
        file_path = os.path.join(folder_path, filename)

        if "2021" not in filename:
            # SEIFA index
            if "sa1" in filename:
                csv_df = sa1_csv_df
                csv_16_column = "SA1_MAINCODE_2016"
                csv_21_column = "SA1_CODE_2021"
                shp_16_field = "SA1_MAIN16"
                shp_21_field = "SA1_CODE21"
                exclude_division_field_list = ['Shape', 'id', 'sa1_7dig16', 'SA1_MAIN16', 'geometry', "SA1_CODE21"]
                geolevel = "sa1"

            # non SEIFA
            else:
                assert "sa2" in filename
                csv_df = sa2_csv_df
                csv_16_column = "SA2_MAINCODE_2016"
                csv_21_column = "SA2_CODE_2021"
                shp_16_field = "SA2_MAIN16"
                shp_21_field = "SA2_CODE21"
                exclude_division_field_list = ['Shape', 'id', 'sa2_name_2', 'yr', 'SA2_MAIN16', 'STATE_CODE',
                                               'STATE_NAME', 'index', 'state_code', 'state_name', 'sa2_code5d',
                                               'sa2_name16', 'gccsa_code', 'gccsa_name', 'sa4_code16', 'sa4_name16',
                                               'sa3_code16', 'sa3_name16', 'sa2_name16', 'geometry', "SA2_CODE21"]
                geolevel = "sa2"

            ConcordanceMapper(csv_df,
                              study_area_df,
                              csv_16_column,
                              csv_21_column,
                              filename,
                              file_path,
                              shp_16_field,
                              shp_21_field,
                              exclude_division_field_list,
                              output_folder_path,
                              geolevel).map()

        else:
            new_file_name = os.path.basename(filename).replace('.shp', '_2021_concordance.shp')
            new_file_path = os.path.join(output_folder_path, new_file_name)
            gdf = gpd.read_file(file_path)
            gdf.to_file(new_file_path)
