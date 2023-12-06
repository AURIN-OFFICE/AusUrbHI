import json
from typing import Tuple, List, Union
import geopandas as gpd
import pandas as pd


class DisaggregationMapper:
    def __init__(self) -> None:
        with open('population_dicts.json', 'r') as f:
            self.sa2_2_sa1_dict, self.pha_2_sa2_dict = json.load(f)

    @staticmethod
    def formatted_divider(value: Union[str, float],
                          divisor: float) -> float:
        """Divide a field value by a divisor considering format"""
        try:
            value = float(str(value).replace(",", ""))
            return round(value * divisor, 2)
        except ValueError:
            if all(sub not in str(value) for sub in ['~', '-', '**', '*', 'nan']):
                print(f"ValueError Warning: field value is not a number")
            return value

    @staticmethod
    def convert_sa2_gdf_to_sa1(sa2_gdf: gpd.GeoDataFrame,
                               study_area_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        sa2_gdf = sa2_gdf.drop_duplicates()
        merged_df: pd.DataFrame = \
            study_area_gdf[['SA1_CODE21', 'SA2_CODE21']].merge(sa2_gdf, on='SA2_CODE21', how='left')
        merged_gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(merged_df, geometry=study_area_gdf.geometry)
        merged_gdf.crs = 'EPSG:4283'
        return merged_gdf

    def divide_field_values(self,
                            gdf: gpd.GeoDataFrame,
                            exclude_division_field_list: List[str],
                            geolevel: str,
                            division_method: str) -> gpd.GeoDataFrame:
        new_gdf: gpd.GeoDataFrame = gdf.copy()
        for idx, row in new_gdf.iterrows():
            sa1_code: str = row['SA1_CODE21']
            sa2_code: str = row['SA2_CODE21']

            if geolevel == "SA2":
                if division_method == "equal":
                    divisor: float = 1 / len(self.sa2_2_sa1_dict[sa2_code])
                elif division_method == "population":
                    divisor: float = self.sa2_2_sa1_dict[sa2_code][sa1_code]
                else:
                    raise ValueError('Division_method must be either "equal" or "population"')

            elif geolevel == "PHA":
                pha_code: str = row['pha_code']
                if division_method == "equal":
                    divisor: float = \
                        (1 / (len(self.pha_2_sa2_dict[pha_code])) * (1 / len(self.sa2_2_sa1_dict[sa2_code])))
                elif division_method == "population":
                    divisor: float = \
                        self.pha_2_sa2_dict[pha_code][sa2_code] * self.sa2_2_sa1_dict[sa2_code][sa1_code]
                else:
                    raise ValueError('Division_method must be either "equal" or "population"')

            else:
                raise ValueError('Geolevel must be either "SA2" or "PHA"')

            for field in new_gdf.columns:
                if field in exclude_division_field_list:
                    continue
                new_gdf.at[idx, field] = self.formatted_divider(row[field], divisor)

        new_gdf = new_gdf.drop_duplicates()
        return new_gdf
