import os
from tqdm import tqdm
from cleansing_scripts.cleanser import Cleanser

dir_path = "../../../_data/AusUrbHI HVI data unprocessed/ABS 2021"
files = [i for i in os.listdir(dir_path) if i.endswith(".shp")]
for filename in tqdm(files,
                     desc="refine study area and convert to shapefile",
                     total=len(files)):
    full_filepath = os.path.join(dir_path, filename)
    study_area_matching_column = "SA1_CODE21"
    data_matching_column = "SA1_CODE_2"
    Cleanser(full_filepath).refine_by_study_area("2021",
                                                 "../../../_data/AusUrbHI HVI data processed/ABS 2021\\",
                                                 study_area_matching_column,
                                                 data_matching_column)
