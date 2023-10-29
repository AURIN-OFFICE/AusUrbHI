import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from tqdm import tqdm


class EHFAnalyzer:

    def __init__(self):
        self.sa1_centroid_dict = self.creat_sa1_centroid_dict()
        self.output_gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')[['SA1_CODE21', 'geometry']]
        self.ds = xr.open_dataset('../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/'
                                  'EHF_heatwaves____daily.nc')

    @staticmethod
    def creat_sa1_centroid_dict() -> dict:
        """Create a dictionary of SA1 centroids, with SA1_CODE21 as the key and the centroid as the value
        """
        gdf = gpd.read_file('../_data/study area/ausurbhi_study_area_2021.shp')
        sa1_centroid_dict = {}
        for i, row in gdf.iterrows():
            sa1_centroid_dict[row['SA1_CODE21']] = row['geometry'].centroid
        return sa1_centroid_dict

    def analyze(self, year: int) -> None:
        """Get:
        1. the average and maximum EHF
        2. the average heatwave duration, number of heatwave days, and number of extreme heatwave days
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

            if point_data['ends'].mean().item() > 10:
                print(sa1)
                print(point_data['EHF'].values)
                print(round(point_data['EHF'].mean().item(), 2))
                print(round(point_data['EHF'].max().item(), 2))
                print(np.nanmean(point_data['ends']).item())
                print(round(np.nanmean(point_data['ends']).item(), 2))
                print(point_data['event'].values)
                print(round(point_data['event'].sum().item(), 2))
                print("-----------------------------")

            data[sa1] = {
                avg_ehf_field: round(point_data['EHF'].mean().item(), 2),
                max_ehf_field: round(point_data['EHF'].max().item(), 2),
                avg_heatwave_duration_field: round(np.nanmean(point_data['ends']).item(), 2),
                number_heatwave_days_field: round(point_data['event'].sum().item(), 2)
            }

        # add the data to the output shapefile in the new added fields
        for sa1_code, values in data.items():
            for i in [avg_ehf_field, max_ehf_field, avg_heatwave_duration_field, number_heatwave_days_field]:
                self.output_gdf.loc[self.output_gdf['SA1_CODE21'] == sa1_code, i] = values[i]


if __name__ == '__main__':
    analyzer = EHFAnalyzer()
    # analyzer.analyze(16)
    analyzer.analyze(21)
    analyzer.output_gdf.to_file('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/heatwave_analysis.shp')
