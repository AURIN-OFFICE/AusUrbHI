import ee
import pandas as pd
import geopandas as gpd
import xarray as xr
import numpy as np
from datetime import datetime, timedelta


class ModisLST:
    def __init__(self,
                 study_area_shapefile: str,
                 start_date: str,
                 end_date: str,
                 shp_region_column: str):

        # authenticate Google Earth Engine and get Modis boundary_data
        ee.Authenticate()
        ee.Initialize()
        self.modis_data = ee.ImageCollection('MODIS/006/MOD11A1')

        # input boundary_data
        self.shp = gpd.read_file(study_area_shapefile)
        self.s_date = start_date
        self.e_date = end_date
        self.region_col = shp_region_column

        # boundary_data cube for storing the output boundary_data
        self.data_cube = xr.DataArray(
            data=[],
            coords={"SA1": [], "time": [], "temperature": ["min_temperature", "max_temperature"]},
            dims=["SA1", "time", "temperature"],
        )

    def get_temperature_data(self):
        for index, row in self.shp.iterrows():
            sa1 = row['SA1_MAIN16']
            geometry = ee.Geometry.Polygon(list(row['geometry'].exterior.coords))

            for year in range(self.start_year, self.end_year + 1):
                for month in range(1, 13):
                    start_date = datetime(year, month, 1)
                    end_date = start_date + timedelta(days=31)
                    date_range = ee.DateRange(ee.Date(start_date), ee.Date(end_date))

                    filtered_data = dataset.filterDate(date_range).filterBounds(geometry)
                    min_temp = filtered_data.min().select('LST_Day_1km', 'LST_Night_1km')
                    max_temp = filtered_data.max().select('LST_Day_1km', 'LST_Night_1km')

                    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days)]
                    for date in dates:
                        temp_data = [{
                            'SA1': sa1,
                            'Date': date,
                            'Min_Temperature': min_temp,
                            'Max_Temperature': max_temp
                        }]
                        self.temp_data = pd.concat(
                            [
                                self.temp_data,
                                pd.DataFrame.from_dict(temp_data)
                            ],
                            ignore_index=True)

    def append_to_data_cube(self, sa1, date, min_temperature, max_temperature):
        new_data = xr.DataArray(
            np.array([[[min_temperature, max_temperature]]]),
            coords={"SA1": [sa1], "time": [date], "temperature": ["min_temperature", "max_temperature"]},
            dims=["SA1", "time", "temperature"],
        )

        if sa1 not in self.data_cube.SA1:
            data_cube = xr.concat([self.data_cube, new_data], dim="SA1")
        elif date not in self.data_cube.time:
            data_cube = xr.concat([self.data_cube, new_data], dim="time")
        else:
            self.data_cube.loc[sa1, date, :] = [min_temperature, max_temperature]
        return data_cube

    def query_temperature(self, sa1, date):
        result = self.temp_data.loc[(self.temp_data['SA1'] == sa1) & (self.temp_data['Date'] == date)]
        return result[['Min_Temperature', 'Max_Temperature']]


obj = ModisLST('boundary_data/sa1_nsw.shp', '2011-01-01', '2021-12-31', 'SA1_MAIN16')
obj.get_data()
print(obj.query_data('10602111401', datetime(2013, 5, 20)))
