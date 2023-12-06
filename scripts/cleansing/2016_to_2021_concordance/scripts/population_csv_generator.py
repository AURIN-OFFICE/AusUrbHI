import geopandas as gpd
from tqdm import tqdm
import json


def create_sa1_population_dict(sa1_population_gdf):
    sa1_population_dict = {}
    for _, row in tqdm(sa1_population_gdf.iterrows(),
                       total=len(sa1_population_gdf), desc="SA1 population"):
        sa1_code_21 = row['SA1_CODE21']
        population = row['Tot_P_P']
        sa1_population_dict[sa1_code_21] = population
    return sa1_population_dict


def create_sa1_in_sa2_dict(sa1_in_sa2_gdf):
    sa1_in_sa2_dict = {}
    for _, row in tqdm(sa1_in_sa2_gdf.iterrows(),
                       total=len(sa1_in_sa2_gdf), desc="SA1 in SA2"):
        sa1_code_21 = row['SA1_CODE21']
        sa2_code_21 = row['SA2_CODE21']
        if sa2_code_21 not in sa1_in_sa2_dict:
            sa1_in_sa2_dict[sa2_code_21] = []
        sa1_in_sa2_dict[sa2_code_21].append(sa1_code_21)
    return {k: set(v) for k, v in sa1_in_sa2_dict.items()}


def create_sa2_population_dict(sa1_population_dict, sa1_in_sa2_dict):
    sa2_population_dict = {}
    for sa2_code, sa1_codes in sa1_in_sa2_dict.items():
        total_population = 0
        for sa1_code in sa1_codes:
            total_population += sa1_population_dict.get(sa1_code, 0)
        sa2_population_dict[sa2_code] = total_population
    return sa2_population_dict


if __name__ == '__main__':
    sa1_population_gdf = gpd.read_file("../../../_data/AusUrbHI HVI data processed/ABS 2021/"
                                       "main_G01_SA1_2021_NSW_study_area_refined.shp")
    sa1_in_sa2_gdf = gpd.read_file("../../../_data/study area/ausurbhi_study_area_2021.shp")

    sa1_population_dict = create_sa1_population_dict(sa1_population_gdf)
    sa1_in_sa2_dict = create_sa1_in_sa2_dict(sa1_in_sa2_gdf)
    sa2_population_dict = create_sa2_population_dict(sa1_population_dict, sa1_in_sa2_dict)

    with open('sa1_population_dict.json', 'w') as f:
        json.dump(sa1_population_dict, f)

    with open('sa2_population_dict.json', 'w') as f:
        json.dump(sa2_population_dict, f)
