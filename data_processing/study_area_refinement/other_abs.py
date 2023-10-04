import os
from tqdm import tqdm
from cleansing_scripts.cleanser import Cleanser

dir_path = "..\\..\\_data\\AusUrbHI HVI data unprocessed\\other ABS datasets"
files = [i for i in os.listdir(dir_path) if i.endswith((".json", ".geojson", ".shp"))]
for filename in tqdm(files,
                     desc="refine study area and convert to shapefile",
                     total=len(files)):
    full_filepath = os.path.join(dir_path, filename)

    if "2021" in filename:
        year = "2021"
    else:
        year = "2016"

    # SEIFA index
    if "sa1" in filename:
        if "2021" in filename:
            study_area_matching_column = "SA1_CODE21"
            data_matching_column = "SA1_CODE21"
        elif "2016" in filename:
            study_area_matching_column = "SA1_MAIN16"
            data_matching_column = "sa1_main16"
        elif "2011" in filename:
            study_area_matching_column = "SA1_MAIN16"
            data_matching_column = "sa1_code"
        else:
            raise ValueError("sa1 for non-seifa or invalid seifa year.")
    # non SEIFA
    else:
        assert "sa2" in filename
        if "2021" in filename:
            study_area_matching_column = "SA2_CODE21"
            data_matching_column = "SA2_CODE21"
        elif "data_by_region" in filename:
            study_area_matching_column = "SA2_MAIN16"
            data_matching_column = "sa2_maincode_2016"
        elif "2020" in filename:
            study_area_matching_column = "SA2_MAIN16"
            data_matching_column = "SA2_MAINCODE_2016"
        else:
            study_area_matching_column = "SA2_MAIN16"
            data_matching_column = "sa2_main16"

    Cleanser(full_filepath).refine_by_study_area(year,
                                                 "..\\..\\_data\\AusUrbHI HVI data processed\\other ABS datasets\\",
                                                 study_area_matching_column,
                                                 data_matching_column)

