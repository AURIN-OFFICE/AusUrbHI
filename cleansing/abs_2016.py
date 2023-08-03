import os
from tqdm import tqdm
from cleansing_scripts.cleanser import Cleanser

dir_path = "../_data/AusUrbHI HVI data unprocessed/ABS 2016"
files = [i for i in os.listdir(dir_path) if i.endswith(".json")]
for filename in tqdm(files,
                     desc="refine study area and convert to shapefile",
                     total=len(files)):
    full_filepath = os.path.join(dir_path, filename)
    Cleanser(full_filepath).refine_by_study_area(2016, "../_data/AusUrbHI HVI data processed/ABS 2016")
