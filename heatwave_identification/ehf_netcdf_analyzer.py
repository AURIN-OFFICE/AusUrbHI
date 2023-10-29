import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
import warnings
from tqdm import tqdm
from contextlib import contextmanager
from collections import defaultdict


@contextmanager
def ignore_specific_warning(message_contains):
    with warnings.catch_warnings(record=True) as w:
        # Trigger a warning.
        warnings.simplefilter("always")
        yield
        for warning in w:
            if message_contains in str(warning.message):
                continue
            warnings.showwarning(
                warning.message, warning.category,
                warning.filename, warning.lineno)


class EHFAnalyzer:

    def __init__(self):
        self.sa1_centroid_dict = self._creat_sa1_centroid_dict()
        self.ds = xr.open_dataset('../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/'
                                  'EHF_heatwaves____daily.nc')
        self.output_gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')[['SA1_CODE21', 'geometry']]
        self.heatwave_days = None
        self.extreme_heatwave_days = None

    @staticmethod
    def _creat_sa1_centroid_dict() -> dict:
        """Create a dictionary of SA1 centroids, with SA1_CODE21 as the key and the centroid as the value
        """
        gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')
        sa1_centroid_dict = {}
        for i, row in gdf.iterrows():
            sa1_centroid_dict[row['SA1_CODE21']] = row['geometry'].centroid
        return sa1_centroid_dict

    def ehf_statistics_analysis(self, start_year: int = 11, end_year: int = 21) -> None:
        """Compute for each year and SA1:
        1. the average and maximum EHF
        2. the average heatwave duration, number of heatwave days, and
        3. number of extreme heatwave days
        for each SA1 centroid location during summer months (Dec, Jan, Feb) in each year.
        """
        for year in range(start_year, end_year + 1):
            ds_summer = self.ds.sel(time=slice(f'20{year-1}-12-01', f'20{year}-02-28'))

            # initiate new fields
            avg_ehf_field = f'avg_ehf_{year}'
            max_ehf_field = f'max_ehf_{year}'
            avg_heatwave_duration_field = f'hw_len_{year}'
            number_heatwave_days_field = f'hw_days_{year}'
            number_extreme_heatwave_days_field = f'ex_hw_{year}'
            for i in [avg_ehf_field, max_ehf_field, avg_heatwave_duration_field, number_heatwave_days_field]:
                self.output_gdf[i] = pd.NA

            # get relevant data for each SA1 centroid location during the period
            year_data = {}
            for sa1, centroid in tqdm(self.sa1_centroid_dict.items(),
                                      total=len(self.sa1_centroid_dict),
                                      desc=f'Computing heatwave statistics for {year}',
                                      colour="green"):
                x, y = centroid.x, centroid.y
                while True:
                    point_data = ds_summer.sel(lon=x, lat=y, method='nearest')
                    if point_data['EHF'].isnull().all():
                        x -= 0.05
                    else:
                        break

                # prepare data
                heatwave_array_in_days = (point_data['ends'][point_data['ends'] != np.timedelta64(0)]
                                          / np.timedelta64(1, 'D'))
                number_heatwave_days = round(heatwave_array_in_days.mean().item(), 2)
                extreme_heatwave_condition = (point_data['event'] == 1) & (point_data['EHF'] >= 3)

                # populate field value dict
                year_data[sa1] = {
                    avg_ehf_field: round(point_data['EHF'].mean().item(), 2),
                    max_ehf_field: round(point_data['EHF'].max().item(), 2),
                    avg_heatwave_duration_field: number_heatwave_days if not np.isnan(number_heatwave_days) else 0,
                    number_heatwave_days_field: round(point_data['event'].sum().item(), 2),
                    number_extreme_heatwave_days_field: round(extreme_heatwave_condition.sum().item(), 2)
                }

            # add the data to the output shapefile in the new added fields
            for sa1_code, values in year_data.items():
                for i in [avg_ehf_field, max_ehf_field, avg_heatwave_duration_field,
                          number_heatwave_days_field, number_extreme_heatwave_days_field]:
                    self.output_gdf.loc[self.output_gdf['SA1_CODE21'] == sa1_code, i] = values[i]

    def get_all_heatwave_days(self, start_year: int = 11, end_year: int = 21) -> None:
        """Compute for each year and SA1:
        1. the dates of heatwaves, and
        2. the dates of extreme heatwaves (EHF >=3)
        for each SA1 centroid location during summer months (Dec, Jan, Feb) in each year.
        """
        # Ensure self.ds['time'] is a DataArray and convert its values

        heatwave_days = defaultdict(dict)
        extreme_heatwave_days = defaultdict(dict)

        for year in range(start_year, end_year + 1):
            ds_summer = self.ds.sel(time=slice(f'20{year - 1}-12-01', f'20{year}-02-28'))

            for sa1, centroid in tqdm(self.sa1_centroid_dict.items(),
                                      total=len(self.sa1_centroid_dict),
                                      desc=f'Collecting heatwave days for {year}',
                                      colour='green'):
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
    with ignore_specific_warning("has multiple fill values {-888.88, -999.99}"):
        analyzer = EHFAnalyzer()

        analyzer.ehf_statistics_analysis()
        analyzer.output_gdf.to_file('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/'
                                    'heatwave_analysis.shp')

        analyzer.get_all_heatwave_days()
        analyzer.heatwave_days.to_csv('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/'
                                      'heatwave_days.csv')
        analyzer.extreme_heatwave_days.to_csv('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/'
                                              'extreme_heatwave_days.csv')
