import os
from tqdm import tqdm
from cleansing_scripts.cleanser import Cleanser

dir_path = "..\\_data\\AusUrbHI HVI data unprocessed\\PHIDU and NATSEM datasets"
files = [i for i in os.listdir(dir_path) if i.endswith(".json")]
for filename in tqdm(files,
                     desc="refine study area and convert to shapefile",
                     total=len(files)):
    full_filepath = os.path.join(dir_path, filename)

    # NATSEM
    if "sa2" in filename:
        study_area_matching_column = "SA2_MAIN16"
        data_matching_column = "sa2_code16"
    # PHIDU
    else:
        assert "pha" in filename

    Cleanser(full_filepath).refine_by_study_area("2016",
                                                 "..\\_data\\AusUrbHI HVI data processed\\PHIDU and NATSEM datasets\\",
                                                 study_area_matching_column,
                                                 data_matching_column)
