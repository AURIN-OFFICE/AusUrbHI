import os
import pandas as pd
import geopandas as gpd
from scripts.concordance_mapper import ConcordanceMapper

csv_16_column = "SA2_MAINCODE_2016"
csv_21_column = "SA2_CODE_2021"
shp_16_field = "SA2_MAIN16"
shp_21_field = "SA2_CODE21"
output_folder_path = "../../_data/AusUrbHI HVI data processed/PHIDU and NATSEM datasets by 2021 concordance"
geolevel = "sa2"

csv_path = "../../_data/study area/CG_SA2_2016_SA2_2021.csv"
csv_df = pd.read_csv(csv_path)

study_area_path = "../../_data/study area/ausurbhi_study_area_2021.shp"
study_area_df = gpd.read_file(study_area_path)

folder_path = "../../_data/AusUrbHI HVI data processed/PHIDU and NATSEM datasets"
for filename in os.listdir(folder_path):
    if filename.endswith(".shp"):
        file_path = os.path.join(folder_path, filename)

        if "phidu" in filename:
            exclude_division_field_list = ['Shape', 'id', 'fid', 'pha_code', 'pha_name', 'SA2_MAIN16', 'geometry', "SA2_CODE21"]
        else:
            exclude_division_field_list = ['Shape', 'id', 'SA2_MAIN16', 'sa2_name16', 'geometry', "SA2_CODE21"]

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
