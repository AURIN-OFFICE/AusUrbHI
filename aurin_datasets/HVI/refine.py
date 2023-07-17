import os
import geopandas as gpd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

#
def refine_abs_2016():
    boundary_file = "../../_data/boundary_data/sa1_nsw.shp"
    boundary_data = gpd.read_file(boundary_file)
    boundary_matching_column = "SA1_MAIN16"
    assert boundary_matching_column in boundary_data.columns

    data_folder = "../../_data/AusUrbHI HVI data raw/ABS 2016/"
    data_files = [f for f in os.listdir(data_folder) if f.endswith('.json')]
    assert len(data_files) == 18
    data_matching_column = "sa1_main16"

    for data_file in tqdm(data_files, desc="refine_abs_2016"):
        data = gpd.read_file(data_folder + data_file)
        assert data_matching_column in data.columns
        assert data['data_matching_column'].isin(boundary_data['boundary_matching_column']).all(), \
            f"Not all values from {data_matching_column} are present."

        output_file = "../../_data/AusUrbHI HVI data study area refined/ABS 2016" \
                      + data_file[45:].split('.')[0] + ".shp"
        refined_data = data[data[data_matching_column].isin(boundary_data[boundary_matching_column])]
        refined_data.to_file(output_file)


def refine_abs_2021():
    boundary_file = "../../_data/boundary_data/sa1_nsw.shp"
    boundary_data = gpd.read_file(boundary_file)
    boundary_matching_column = "SA1_MAIN16"
    assert boundary_matching_column in boundary_data.columns

    data_folder = "../../_data/AusUrbHI HVI data raw/ABS 2021/"
    data_files = [f for f in os.listdir(data_folder) if f.endswith('.shp')]
    assert len(data_files) == 18
    data_matching_column = "SA1_CODE_2"

    for data_file in tqdm(data_files, desc="refine_abs_2021"):
        data = gpd.read_file(data_folder + data_file)
        assert data_matching_column in data.columns
        assert data['data_matching_column'].isin(boundary_data['boundary_matching_column']).all(), \
            f"Not all values from {data_matching_column} are present."

        output_file = "../../_data/AusUrbHI HVI data study area refined/ABS 2021" \
                      + data_file[5:].split('.')[0] + ".shp"
        refined_data = data[data[data_matching_column].isin(boundary_data[boundary_matching_column])]
        refined_data.to_file(output_file)


def refine_other_abs():
    pass


def phidu_natsem():
    pass


if __name__ == "__main__":
    # refine_abs_2016()
    # refine_abs_2021()
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(refine_abs_2016)
        executor.submit(refine_abs_2021)
