import os
import geopandas as gpd
from tqdm import tqdm
from concordance_mapper import ConcordanceMapper

mapper = ConcordanceMapper()

# create a dictionary of pha codes and number of sa2s in each pha
pha_has_number_of_sa2_dict = mapper.create_pha_has_number_of_sa2_dict()

# create a dictionary of sa2 codes and number of sa1s in each sa2
sa2_has_number_of_sa1_dict = mapper.create_sa2_has_number_of_sa1_dict()

# divide phidu data value by number of sa2s in pha
folder_path = "../_data/AusUrbHI HVI data processed/PHIDU and NATSEM datasets by 2021 concordance"
for filename in tqdm(os.listdir(folder_path), total=len(os.listdir(folder_path)), desc="processing files", position=0):
    if filename.endswith(".shp"):
        file_path = os.path.join(folder_path, filename)

        if "phidu" in filename:
            # divide phidu data value by number of sa2s in pha
            exclude_division_field_list = ['Shape', 'id', 'fid_1', 'pha_code', 'pha_name', 'SA2_MAIN16', 'geometry']
            gdf = gpd.read_file(file_path)
            pha_2_sa2_gdf = mapper.divide_pha_data_by_number_of_sa2(gdf, exclude_division_field_list, filename)

            # convert sa2 shp to sa1 shp

            # divide sa2 data value by number of sa1s in sa2

        else:
            # convert sa2 shp to sa1 shp

            # divide sa2 data value by number of sa1s in sa2
            exclude_division_field_list = ['Shape', 'id', 'SA2_MAIN16', 'sa2_name16', 'geometry']