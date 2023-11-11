import os
import pandas as pd
import geopandas as gpd
from scripts.concordance_mapper import ConcordanceMapper

csv_16_column = "SA1_MAINCODE_2016"
csv_21_column = "SA1_CODE_2021"
shp_16_field = "SA1_MAIN16"
shp_21_field = "SA1_CODE21"
exclude_division_field_list = ['Shape', 'id', 'SA1_MAIN16', 'sa1_7dig16', 'geometry', "SA1_CODE21"]
output_folder_path = "../../_data/AusUrbHI HVI data processed/ABS 2016 by 2021 concordance"
geolevel = 'sa1'

csv_path = "../../_data/study area/CG_SA1_2016_SA1_2021.csv"
csv_df = pd.read_csv(csv_path)

study_area_path = "../../_data/study area/ausurbhi_study_area_2021.shp"
study_area_df = gpd.read_file(study_area_path)

folder_path = "../../_data/AusUrbHI HVI data processed/ABS 2016"
for filename in os.listdir(folder_path):
    if filename.endswith(".shp"):
        file_path = os.path.join(folder_path, filename)
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
