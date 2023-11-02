import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from tqdm import tqdm
from collections import defaultdict
from scipy.stats import rankdata


class EHFAnalyzer:

    def __init__(self):
        self.sa1_centroid_dict = self._creat_sa1_centroid_dict()
        self.ehf_xarray = xr.open_dataset('../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/'
                                          'EHF_heatwaves____daily.nc')
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

    @staticmethod
    def _compute_average_heatwave_duration(point_data_ends: xr.DataArray) -> float:
        """The input is a heatwave length xarray data like [0, 3, 0, 0, 0, 2, 0, 0]. The function finds the average
        non-zero values in the list. In this case 2.5. The hard part is dealing with timedelta and nan values.
        """
        heatwave_array_in_days = (point_data_ends[point_data_ends != np.timedelta64(0)]
                                  / np.timedelta64(1, 'D'))
        average_duration = heatwave_array_in_days.mean().item()
        return average_duration if not np.isnan(average_duration) else 0

    @staticmethod
    def _compute_average_excess_heat_duration(point_data_ehf: xr.DataArray) -> float:
        """The input is a EHF value xarray data like [0, 1, 3, 2, 0, 0, 1, 1]. The function finds the average length
        of consecutive non-zero values in the list. For example 1, 3, 2, and 1, 1. So the result will be 2.5.
        """
        segment_lengths = []
        current_length = 0

        for value in point_data_ehf:
            if value != 0:
                current_length += 1
            elif current_length != 0:
                # If we hit a zero after a non-zero segment, save the segment length and reset
                segment_lengths.append(current_length)
                current_length = 0

        # Check if the last segment is a non-zero segment and wasn't added
        if current_length != 0:
            segment_lengths.append(current_length)

        return sum(segment_lengths) / len(segment_lengths) if segment_lengths else 0

    def ehf_statistics_analysis(self, years: list = (16, 21)) -> None:
        """Compute for each year and SA1:
        1. the average and maximum EHF,
        2. the average heatwave duration, number of heatwave days,
        3. average excess heat duration and number of excess heat days (EHF > 0), and
        4. number of extreme heatwave days
        for each SA1 centroid location during summer months (Dec, Jan, Feb) in each year.
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

            number_of_extreme_heatwave_days = f'ex_days_{year}'

            # get relevant data for each SA1 centroid location during the period
            year_data = {}
            for sa1, centroid in tqdm(self.sa1_centroid_dict.items(),
                                      total=len(self.sa1_centroid_dict),
                                      desc=f'Computing heatwave statistics for year 20{year}',
                                      colour="cyan"):
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

    def percentile_deviation_analysis(self,
                                      ref_years: range = range(2010, 2016),
                                      target_years: tuple = (2016, 2021)):
        """
        Objective by instruction:
        1. Create raster of "average daily temperature" using maximum and minimum daily temperature rasters across the
        study area during the summer period for the years 2010-2015, 2016, and 2021.
        2. Create spatial "average daily temperature" data for each SA1 in the study area over the above years.
        3. Create two separate data sets of daily temperature: 2010-2015+2016, and 2010-2015+2021
        4. For each area (should be ~2555 rows, give or take for leap years), convert "average daily temperature" into
        percentiles.
        5. For 2016 and 2021 summer periods, produce both the average percentile and the maximum percentile per region.
        """

        # Compute the average temperature data
        avg_xr = (self.max_xr['max_temp'] + self.min_xr['min_temp']) / 2

        for target_year in target_years:

            # Concatenate summer periods for all reference year + target year
            years = [i for i in ref_years] + [target_year]
            summer_datasets = [avg_xr.sel(time=slice(f'{year-1}-12-01', f'{year}-02-28')) for year in years]
            all_summers_concatenated = xr.concat(summer_datasets, dim='time')

            # Compute xarray of average temperatures for each SA1 on each day
            for sa1_code, centroid in tqdm(self.sa1_centroid_dict.items(),
                                           total=len(self.sa1_centroid_dict),
                                           desc='Computing average and maximum percentile deviation for each SA1',
                                           colour="cyan"):
                x, y = centroid.x, centroid.y
                while True:
                    sa1_data = all_summers_concatenated.sel(lon=x, lat=y, method='nearest')
                    if sa1_data.isnull().all():
                        x -= 0.05
                    else:
                        break

                # Convert to percentile
                percentiles = rankdata(sa1_data, method='average') / len(sa1_data) * 100
                sa1_percentiles = xr.DataArray(percentiles, dims=sa1_data.dims, coords=sa1_data.coords)

                # Get average and maximum percentile for the target year
                percentiles_target_year = sa1_percentiles.sel(
                    time=slice(f'{target_year-1}-12-01', f'{target_year}-02-28'))
                assert percentiles_target_year.size == 90, f"Data size does not match."
                max_percentile = round(percentiles_target_year.max().item(), 2)
                avg_percentile = round(percentiles_target_year.mean().item(), 2)

                # Update shapefile
                self.output_gdf.loc[self.output_gdf['SA1_CODE21'] ==
                                    sa1_code, f"avg_dev_{target_year-2000}"] = avg_percentile
                self.output_gdf.loc[self.output_gdf['SA1_CODE21'] ==
                                    sa1_code, f"max_dev_{target_year-2000}"] = max_percentile

    def get_all_heatwave_days(self, start_year: int = 11, end_year: int = 22) -> None:
        """Compute for each year and SA1:
        1. the dates of heatwaves, and
        2. the dates of extreme heatwaves (EHF >=3)
        for each SA1 centroid location during summer months (Dec, Jan, Feb) in each year.
        """
        # Ensure self.ehf_xarray['time'] is a DataArray and convert its values

        heatwave_days = defaultdict(dict)
        extreme_heatwave_days = defaultdict(dict)

        for year in range(start_year, end_year + 1):
            ds_summer = self.ehf_xarray.sel(time=slice(f'20{year - 1}-12-01', f'20{year}-02-28'))

            for sa1, centroid in tqdm(self.sa1_centroid_dict.items(),
                                      total=len(self.sa1_centroid_dict),
                                      desc=f'Collecting heatwave days for year 20{year}',
                                      colour='cyan'):
                x, y = centroid.x, centroid.y
                while True:
                    point_data = ds_summer.sel(lon=x, lat=y, method='nearest')
                    if point_data['EHF'].isnull().all():
                        x -= 0.05
                    else:
                        break

                # Heatwave days (event == 1)
                heatwave_dates = \
                    (point_data.where(point_data['event'] == 1)
                     .dropna(dim='time', how='all')
                     .time.values)

                # Extreme heatwave days (EHF >= 3)
                extreme_heatwave_dates = \
                    (point_data.where((point_data['event'] == 1) & (point_data['EHF'] >= 3))
                     .dropna(dim='time', how='all')
                     .time.values)

                heatwave_days[sa1][year] = ', '.join([date.strftime('%Y-%m-%d') for date in heatwave_dates])
                extreme_heatwave_days[sa1][year] = ', '.join([date.strftime('%Y-%m-%d') for date in
                                                              extreme_heatwave_dates])

        # Convert dictionaries to DataFrame and save as CSV
        self.heatwave_days = pd.DataFrame.from_dict(heatwave_days, orient='index')
        self.extreme_heatwave_days = pd.DataFrame.from_dict(extreme_heatwave_days, orient='index')


if __name__ == '__main__':
    analyzer = EHFAnalyzer()

    analyzer.ehf_statistics_analysis()
    analyzer.percentile_deviation_analysis()
    new_column_order = [
        'avg_dev_16', 'max_dev_16', 'avg_ehf_16', 'max_ehf_16', 'hw_len_16', 'hw_days_16',
        'eh_len_16', 'eh_days_16', 'ex_days_16', 'avg_dev_21', 'max_dev_21', 'avg_ehf_21',
        'max_ehf_21', 'hw_len_21', 'hw_days_21', 'eh_len_21', 'eh_days_21', 'ex_days_21', 'geometry'
    ]
    analyzer.output_gdf = analyzer.output_gdf[new_column_order]
    analyzer.output_gdf.to_file('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/'
                                'heatwave_analysis.shp')

    # analyzer.get_all_heatwave_days()
    # analyzer.heatwave_days.to_csv('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/'
    #                               'heatwave_days.csv')
    # analyzer.extreme_heatwave_days.to_csv('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/'
    #                                       'extreme_heatwave_days.csv')
