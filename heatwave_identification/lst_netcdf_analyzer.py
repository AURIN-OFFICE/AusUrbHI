import pandas as pd
import geopandas as gpd
import xarray as xr
import numpy as np
from tqdm import tqdm
from xarray import concat
from collections import defaultdict
from pprint import pprint


class LSTAnalyzer:
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

    def __init__(self):
        self.sa1_centroid_dict = self._creat_sa1_centroid_dict()
        self.max_xr = xr.open_dataset('../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/'
                                      '2010_2022_max_temp_clipped.nc')
        self.min_xr = xr.open_dataset('../_data/AusUrbHI HVI data unprocessed/Longpaddock SILO LST/'
                                      '2010_2022_min_temp_clipped.nc')
        self.avg_xr = (self.max_xr['max_temp'] + self.min_xr['min_temp']) / 2
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

    def calculate_average_summer_temperature_percentile_reference_period(self, years: range = range(2010, 2016)):
        """
        Calculate and return the percentile of the average summer temperatures for each SA1 region
        during the specified reference period.
        :return: {SA1_CODE21: percentile}
        """

        # Concatenate summer periods for all years
        summer_datasets = [self.avg_xr.sel(time=slice(f'{year - 1}-12-01', f'{year}-02-28')) for year in years]
        all_summers_concatenated = concat(summer_datasets, dim='time')

        # Compute average temperatures for each SA1
        sa1_avg_summer_temp_dict = {}
        for sa1, centroid in tqdm(self.sa1_centroid_dict.items(), total=len(self.sa1_centroid_dict),
                                  desc='Computing SA1 average summer temperatures', colour="green"):
            x, y = centroid.x, centroid.y
            while True:
                sa1_data = all_summers_concatenated.sel(lon=x, lat=y, method='nearest')
                if sa1_data.isnull().all():
                    x -= 0.05
                else:
                    break
            sa1_avg_summer_temp_dict[sa1] = [round(sa1_data.mean().item(), 2), round(sa1_data.max().item(), 2)]

        # # Calculate percentiles
        # values = list(sa1_avg_summer_temp_dict.values())
        # sa1_temp_percentiles = {}
        # for key, value in sa1_avg_summer_temp_dict.items():
        #     percentile_formula = (100 * (1 - (values.count(value) - values.index(value)) / len(values)))
        #     percentile = np.clip(percentile_formula, 1, 100)
        #     percentile_value = np.percentile(values, percentile)
        #     sa1_temp_percentiles[key] = int(round(percentile_value))
        return sa1_avg_summer_temp_dict

    def calculate_percentiles(self, summer_temps_df):
        # Calculate percentile ranks
        summer_temps_df['percentile'] = summer_temps_df['avg_temp'].rank(pct=True) * 100
        return summer_temps_df

    def calculate_deviation(self, ref_df, current_df):
        # Merging on SA1 code to align the data
        merged_df = ref_df.merge(current_df, on='SA1_CODE21', suffixes=('_ref', '_curr'))

        # Calculating deviation
        merged_df['percentile_deviation'] = merged_df['percentile_curr'] - merged_df['percentile_ref']
        return merged_df

    def percentile_deviation_analysis(
            self, ref_years: range = range(2010, 2016),
            current_years: tuple = (2016, 2021)):

        # Calculate reference period stats
        ref_temps = [self.calculate_summer_temps(year) for year in ref_years]
        ref_avg = pd.concat(ref_temps).groupby('SA1_CODE21').mean()  # Adjust depending on the actual structure
        ref_percentiles = self.calculate_percentiles(ref_avg)

        # Analyze specific years
        for year in current_years:
            # Calculate summer temperatures and percentiles
            current_temps = self.calculate_summer_temps(year)
            current_percentiles = self.calculate_percentiles(current_temps)

            # Calculate deviation
            deviation = self.calculate_deviation(ref_percentiles, current_percentiles)

            # Output or store the results
            # This part depends on how you want to use or store the final data
            # For example, you might want to write it to a file or database, or just print it
            print(f"Deviation for {year}:")
            print(deviation)


if __name__ == '__main__':
    analyzer = LSTAnalyzer()

    # analyzer.percentile_deviation_analysis()
    # analyzer.output_gdf.to_file('../_data/AusUrbHI HVI data processed/Longpaddock SILO LST/'
    #                             'percentile_deviation.shp')

    pprint(analyzer.calculate_average_summer_temperature_percentile_reference_period())
