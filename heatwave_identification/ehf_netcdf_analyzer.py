import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from tqdm import tqdm


class EHFAnalyzer:

    def __init__(self):
        self.sa1_centroid_dict = self._creat_sa1_centroid_dict()
        self.output_gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')[['SA1_CODE21', 'geometry']]
        self.ds = xr.open_dataset('../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/'
                                  'EHF_heatwaves____daily.nc')

    @staticmethod
    def _creat_sa1_centroid_dict() -> dict:
        """Create a dictionary of SA1 centroids, with SA1_CODE21 as the key and the centroid as the value
        """
        gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')
        sa1_centroid_dict = {}
        for i, row in gdf.iterrows():
            sa1_centroid_dict[row['SA1_CODE21']] = row['geometry'].centroid
        return sa1_centroid_dict

    def complete_analyze(self, year: int) -> None:
        """Get:
        1. the average and maximum EHF
        2. the average heatwave duration, number of heatwave days, and
        3. number of extreme heatwave days
        for each SA1 centroid location during summer months (Dec, Jan, Feb) of the given year.
        """
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
        data = {}
        for sa1, centroid in tqdm(self.sa1_centroid_dict.items(),
                                  total=len(self.sa1_centroid_dict),
                                  desc=f'Computing EHF for {year}',
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
            data[sa1] = {
                avg_ehf_field: round(point_data['EHF'].mean().item(), 2),
                max_ehf_field: round(point_data['EHF'].max().item(), 2),
                avg_heatwave_duration_field: number_heatwave_days if not np.isnan(number_heatwave_days) else 0,
                number_heatwave_days_field: round(point_data['event'].sum().item(), 2),
                number_extreme_heatwave_days_field: round(extreme_heatwave_condition.sum().item(), 2)
            }

        # add the data to the output shapefile in the new added fields
        for sa1_code, values in data.items():
            for i in [avg_ehf_field, max_ehf_field, avg_heatwave_duration_field,
                      number_heatwave_days_field, number_extreme_heatwave_days_field]:
                self.output_gdf.loc[self.output_gdf['SA1_CODE21'] == sa1_code, i] = values[i]

    def get_all_heatwave_days(self, start=10, end=22):



if __name__ == '__main__':
    analyzer = EHFAnalyzer()
    # for i in range[10, 23]:
    #     analyzer.complete_analyze(i)
    analyzer.get_all_heatwave_days()
    analyzer.output_gdf.to_file('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/heatwave_analysis.shp')
