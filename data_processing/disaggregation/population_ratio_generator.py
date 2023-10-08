import json
import pandas as pd
import geopandas as gpd
from tqdm import tqdm


class PopulationMapper:
    """
    create dictionaries of population percentage (ratio) of SA1 in SA2, and SA2 in PHA

    :: input ::
    sa1_in_sa2_gdf: | SA1_CODE21 | SA2_CODE21 | ... |
    sa2_2016_in_pha_data: | SA2 code | PHA code | ... |
    sa2_2016_to_sa2_2021_data: | SA2_MAINCODE_2016 | SA2_CODE_2021 | ... |
    sa1_population_gdf: | SA1_CODE21 | Tot_P_P | ... |

    :: temporary data ::
    sa1_population_dict: {SA1_CODE21: population, ...}
    sa1_in_sa2_dict: {SA2_CODE21: (SA1_CODE21, ...), ...}
    sa2_in_pha_dict: {PHA_CODE: (SA2_CODE21, ...), ...}

    :: return ::
    self.sa2_2_sa1_dict = {
        'SA2_CODE21': {
            'SA1_CODE21': SA1_population_ratio_in_SA2,
            ...
        },
        ...
    }
    self.pha_2_sa2_dict = {
        PHA_CODE: {
            SA2_CODE21: SA2_population_ratio_in_PHA,
        },
    }
    """
    def __init__(self):
        self.sa1_population_gdf = gpd.read_file("../../_data/AusUrbHI HVI data processed/ABS 2021/"
                                                "main_G01_SA1_2021_NSW_study_area_refined.shp")
        self.sa1_in_sa2_gdf = gpd.read_file("../../_data/study area/ausurbhi_study_area_2021.shp")
        self.sa2_2016_in_pha_data = pd.read_csv("../../_data/study area/PHIDU_2016_SA2_PHA.csv")
        self.sa2_2016_to_sa2_2021_data = pd.read_csv("../../_data/study area/CG_SA2_2016_SA2_2021.csv")

        self.sa1_population_dict = self.create_sa1_population_dict()
        self.sa1_in_sa2_dict = self.create_sa1_in_sa2_dict()
        self.sa2_in_pha_dict = self.create_sa2_in_pha_dict()

        self.sa1_population_ratio_in_sa2_dict = self.create_sa1_population_ratio_in_sa2_dict()
        self.sa2_population_ratio_in_pha_dict = self.create_sa2_population_ratio_in_pha_dict()

    def create_sa1_population_dict(self):
        sa1_population_dict = {}
        for _, row in tqdm(self.sa1_population_gdf.iterrows(),
                           total=len(self.sa1_population_gdf), desc="SA1 population"):
            sa1_code_21 = row['SA1_CODE21']
            population = row['Tot_P_P']
            sa1_population_dict[sa1_code_21] = population
        return sa1_population_dict

    def create_sa1_in_sa2_dict(self):
        sa1_in_sa2_dict = {}
        for _, row in tqdm(self.sa1_in_sa2_gdf.iterrows(),
                           total=len(self.sa1_in_sa2_gdf), desc="SA1 in SA2"):
            sa1_code_21 = row['SA1_CODE21']
            sa2_code_21 = row['SA2_CODE21']
            if sa2_code_21 not in sa1_in_sa2_dict:
                sa1_in_sa2_dict[sa2_code_21] = []
            sa1_in_sa2_dict[sa2_code_21].append(sa1_code_21)
        return {k: set(v) for k, v in sa1_in_sa2_dict.items()}

    def create_sa2_in_pha_dict(self):
        sa2_in_pha_dict = {}
        for _, row in tqdm(self.sa2_2016_in_pha_data.iterrows(),
                           total=len(self.sa2_2016_in_pha_data), desc="SA2 in PHA"):
            sa2_code_2016 = row['SA2 code']
            pha_code = row['PHA code']
            if pha_code not in sa2_in_pha_dict:
                sa2_in_pha_dict[pha_code] = []
            # convert SA2 2016 code to SA2 2021 code
            sa2_code_2021_list = self.sa2_2016_to_sa2_2021_data[self.sa2_2016_to_sa2_2021_data['SA2_MAINCODE_2016']
                                                                == sa2_code_2016]['SA2_CODE_2021'].tolist()
            sa2_in_pha_dict[pha_code].extend(sa2_code_2021_list)
        return {k: {x for x in v if str(x) != 'nan'} for k, v in sa2_in_pha_dict.items()}

    def create_sa1_population_ratio_in_sa2_dict(self):
        sa1_population_ratio_in_sa2_dict = {}
        for sa2_code, sa1_list in tqdm(self.sa1_in_sa2_dict.items(),
                                       total=len(self.sa1_in_sa2_dict), desc="SA1 Population Ratio in SA2"):
            total_population_sa2 = sum(self.sa1_population_dict[sa1_code] for sa1_code in sa1_list)
            ratio_dict = {}
            for sa1_code in sa1_list:
                if total_population_sa2 == 0:
                    ratio = 1 / len(sa1_list)
                else:
                    ratio = self.sa1_population_dict[sa1_code] / total_population_sa2
                ratio_dict[sa1_code] = ratio
            sa1_population_ratio_in_sa2_dict[sa2_code] = ratio_dict
        return sa1_population_ratio_in_sa2_dict

    def create_sa2_population_ratio_in_pha_dict(self):
        sa2_population_ratio_in_pha_dict = {}
        for pha_code, sa2_list in tqdm(self.sa2_in_pha_dict.items(),
                                       total=len(self.sa2_in_pha_dict), desc="SA2 Population Ratio in PHA"):
            try:
                total_population_pha = sum(
                    sum(self.sa1_population_dict[sa1_code] for sa1_code in self.sa1_in_sa2_dict[sa2_code])
                    for sa2_code in sa2_list)
            except KeyError:
                # PHA (and its SA2s) not in study area
                continue
            ratio_dict = {}
            for sa2_code in sa2_list:
                if total_population_pha == 0:
                    ratio = 1 / len(sa2_list)
                else:
                    sa2_population = sum(self.sa1_population_dict[sa1_code]
                                         for sa1_code in self.sa1_in_sa2_dict[sa2_code])
                    ratio = sa2_population / total_population_pha
                ratio_dict[sa2_code] = ratio
            sa2_population_ratio_in_pha_dict[pha_code] = ratio_dict
        return sa2_population_ratio_in_pha_dict


if __name__ == '__main__':
    mapper = PopulationMapper()
    data = (mapper.sa1_population_ratio_in_sa2_dict,
            mapper.sa2_population_ratio_in_pha_dict)

    try:
        # Assert that the values in sa1_population_ratio_in_sa2_dict sum up to 1
        for sa2_code, ratios in mapper.sa1_population_ratio_in_sa2_dict.items():
            total_ratio = sum(ratios.values())
            assert abs(total_ratio - 1) < 1e-6, f"Total ratio for SA2 code {sa2_code} is not close to 1: {total_ratio}"

        # Assert that the values in sa2_population_ratio_in_pha_dict sum up to 1
        for pha_code, ratios in mapper.sa2_population_ratio_in_pha_dict.items():
            total_ratio = sum(ratios.values())
            assert abs(total_ratio - 1) < 1e-6, f"Total ratio for PHA code {pha_code} is not close to 1: {total_ratio}"
    except Exception as e:
        print(e)

    with open('population_dicts.json', 'w') as f:
        json.dump(data, f)
