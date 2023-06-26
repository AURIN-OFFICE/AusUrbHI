import os
import geopandas as gpd
from tqdm import tqdm


def refine_abs_2016():
    boundary_file = "../../_data/boundary_data/sa1_nsw.shp"
    boundary_data = gpd.read_file(boundary_file)
    boundary_matching_column = "SA1_MAIN16"
    assert boundary_matching_column in boundary_data.columns
    data_matching_column = "sa1_main16"

    data_files = os.listdir("../../_data/AusUrbHI HVI data raw/ABS 2016")
    for data_file in tqdm(data_files, desc="Refining data"):
        data = gpd.read_file("../../_data/AusUrbHI HVI data raw/ABS 2016/" + data_file)
        assert data_matching_column in data.columns
        output_file = "../../_data/AusUrbHI HVI data study area refined/ABS 2016" \
                      + data_file[45:].split('.')[0] + ".shp"
        refined_data = data[data[data_matching_column].isin(boundary_data[boundary_matching_column])]
        refined_data.to_file(output_file)

def refine_abs_2021():
    boundary_file = "../../_data/boundary_data/sa1_nsw.shp"
    boundary_data = gpd.read_file(boundary_file)
    boundary_matching_column = "SA1_MAIN16"
    assert boundary_matching_column in boundary_data.columns
    data_matching_column = "sa1_main16"

    data_files = os.listdir("../../_data/AusUrbHI HVI data raw/ABS 2016")
    for data_file in tqdm(data_files, desc="Refining data"):
        data = gpd.read_file("../../_data/AusUrbHI HVI data raw/ABS 2016/" + data_file)
        assert data_matching_column in data.columns
        output_file = "../../_data/AusUrbHI HVI data study area refined/ABS 2016" \
                      + data_file[45:].split('.')[0] + ".shp"
        refined_data = data[data[data_matching_column].isin(boundary_data[boundary_matching_column])]
        refined_data.to_file(output_file)


if __name__ == "__main__":
    # refine_abs_2016()