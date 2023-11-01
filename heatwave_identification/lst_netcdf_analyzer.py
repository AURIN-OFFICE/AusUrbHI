import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from tqdm import tqdm
from collections import defaultdict


class EHFAnalyzer:
    """
    1. Create raster of "average daily temperature" using maximum and minimum daily temperature rasters across the
    study area during the summer period for the years 2010-2015, 2016, and 2021.
    2. Create spatial "average daily temperature" data for each SA1 in the study area over the above years.
    3. Create two separate data sets of daily temperature: 2010-2015+2016, and 2010-2015+2021
    4. For each area (should be ~2555 rows, give or take for leap years), convert "average daily temperature" into
    percentiles.
    5. For 2016 and 2021 summer periods, produce both the average percentile and the maximum percentile per region.
    """

    def __init__(self):
        self.sa1_centroid_dict = self._creat_sa1_centroid_dict()
        self.max_xr = xr.open_dataset('../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/'
                                      '2010_2022_max_temp_clipped.nc')
        self.min_xr = xr.open_dataset('../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/'
                                      '2010_2022_min_temp_clipped.nc')
        self.output_gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')[['SA1_CODE21', 'geometry']]

    @staticmethod
    def _creat_sa1_centroid_dict() -> dict:
        """Create a dictionary of SA1 centroids, with SA1_CODE21 as the key and the centroid as the value
        """
        gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')
        sa1_centroid_dict = {}
        for i, row in gdf.iterrows():
            sa1_centroid_dict[row['SA1_CODE21']] = row['geometry'].centroid
        return sa1_centroid_dict

    def

    def ehf_statistics_analysis(self, years: list = (16, 21)) -> None:
        """
        """
        for year in years:
            ds_summer = self.ehf_xarray.sel(time=slice(f'20{year-1}-12-01', f'20{year}-02-28'))

            # initiate new fields; explains will be given below
            average_EHF_value = f'avg_ehf_{year}'
            max_EHF_value = f'max_ehf_{year}'

            average_heatwave_duration = f'hw_len_{year}'
            number_of_heatwave_days = f'hw_days_{year}'

            average_excess_heat_duration = f'eh_len_{year}'
            number_of_excess_heat_days = f'eh_days_{year}'

            number_of_extreme_heatwave_days = f'ex_len_{year}'

            # get relevant data for each SA1 centroid location during the period
            year_data = {}
            for sa1, centroid in tqdm(self.sa1_centroid_dict.items(),
                                      total=len(self.sa1_centroid_dict),
                                      desc=f'Computing heatwave statistics for year 20{year}',
                                      colour="green"):
                x, y = centroid.x, centroid.y
                while True:
                    point_data = ds_summer.sel(lon=x, lat=y, method='nearest')
                    if point_data['EHF'].isnull().all():
                        x -= 0.05
                    else:
                        break

                # == populate field value dict ==
                # average_EHF_value: average EHF values
                # max_EHF_value: max EHF value
                # average_heatwave_duration: average of non-zero values in point_data['ends']
                # number_of_heatwave_days: number/sum of non-zero values in point_data['event']
                # average_excess_heat_duration: average lengths of non-zero consecutive values in point_data['EHF']
                # number_of_excess_heat_days: number of non-zero EHF values
                # number_of_extreme_heatwave_days: number of non-zero event value while also EHF >= 3

                assert (point_data['event'].sum().item() ==
                        (point_data['event'] != 0).sum().item(), 'event stats error')

                year_data[sa1] = {
                    average_EHF_value: round(point_data['EHF'].mean().item(), 2),
                    max_EHF_value: round(point_data['EHF'].max().item(), 2),

                    average_heatwave_duration: round(self._compute_average_heatwave_duration(point_data['ends']), 2),
                    number_of_heatwave_days: round(point_data['event'].sum().item(), 2),

                    average_excess_heat_duration: round(
                        self._compute_average_excess_heat_duration(point_data['EHF']), 2),
                    number_of_excess_heat_days: round((point_data['EHF'] != 0).sum().item(), 2),

                    number_of_extreme_heatwave_days: round(
                        ((point_data['event'] == 1) & (point_data['EHF'] >= 3)).sum().item(), 2)
                }

            # add the data to the output shapefile in the new added fields
            for sa1_code, values in year_data.items():
                for i in [average_EHF_value, max_EHF_value, average_excess_heat_duration, number_of_excess_heat_days,
                          average_heatwave_duration, number_of_heatwave_days, number_of_extreme_heatwave_days]:
                    self.output_gdf.loc[self.output_gdf['SA1_CODE21'] == sa1_code, i] = values[i]


if __name__ == '__main__':
    analyzer = EHFAnalyzer()

    analyzer.ehf_statistics_analysis()
    analyzer.output_gdf.to_file('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/'
                                'percentile_deviation.shp')
