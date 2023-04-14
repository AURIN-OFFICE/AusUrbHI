# -*- coding: utf-8 -*-
import ee
import geopandas as gpd
import xarray as xr
from datetime import datetime, timedelta


class ModisLST:
    """
    The ModisLST class is used to retrieve the MODIS Land Surface Temperature (LST) data for a given study area
    and date range. The class uses the Google Earth Engine (GEE) API to retrieve the data and generate a xarray.
    """
    def __init__(self,
                 study_area_shapefile: str,
                 shp_region_column: str,
                 start_date: str,
                 end_date: str):
        """
        @param study_area_shapefile: a shapefile containing multiple polygons of the study area
        @param shp_region_column: the name of the column in the shapefile that contains the region names
        @param start_date: start date of the data to be retrieved
        @param end_date: end date of the data to be retrieved
        """

        # authenticate Google Earth Engine and get the MODIS data
        ee.Authenticate()
        ee.Initialize()
        self.modis_data = ee.ImageCollection('MODIS/006/MOD11A1')

        # input area geometry and date range
        self.shp = gpd.read_file(study_area_shapefile)
        self.region_col = shp_region_column
        self.s_date = start_date
        self.e_date = end_date

        # boundary_data cube for storing the output boundary_data
        self.data_cube = xr.Dataset(
            data_vars={"tmax": [],
                       "tmin": []},
            coords={"region": [],
                    "date": []}
        )

    def get_extreme_temperature_data_area_date(self,
                                               geometry: ee.Geometry,
                                               date: ee.Date) -> (float, float):
        """
        Get the max and min temperature for a given geometry and date
        @param geometry: a geometry object
        @param date: a datetime object
        @return: a tuple of the max and min temperature
        """
        # Define the GEE image processing pipeline
        filtered_lst = self.modis_data\
            .filterDate(date, date.advance(1, 'day'))\
            .filterBounds(geometry)

        # Select temperature bands
        daytime_lst = filtered_lst.select('LST_Day_1km')
        nighttime_lst = filtered_lst.select('LST_Night_1km')

        # Convert to Celsius and reduce to mean
        daytime_lst = daytime_lst.map(lambda img: img.multiply(0.02).subtract(273.15))
        nighttime_lst = nighttime_lst.map(lambda img: img.multiply(0.02).subtract(273.15))

        # Calculate max and min temperature
        tmax = daytime_lst.reduce(ee.Reducer.max()).clip(geometry)
        tmin = nighttime_lst.reduce(ee.Reducer.min()).clip(geometry)
        return tmax, tmin

    def append_to_data_cube(self,
                            region_name: str,
                            date: ee.Date,
                            tmax: str,
                            tmin: str):
        """
        The function appends the temperature data to the data cube
        @param region_name: the name of the region
        @param date: the date of the data
        @param tmax: the max temperature
        @param tmin: the min temperature
        """
        # convert ee.Date to datetime object
        date = datetime.utcfromtimestamp(ee.Date(date).getInfo()['value'] / 1000)

        # create a new dataset and append it to the data cube
        new_data = xr.Dataset(
            data_vars={"tmax": (["region", "date"], [[tmax]]),
                       "tmin": (["region", "date"], [[tmin]])},
            coords={"region": [region_name],
                    "date": [date]}
        )
        self.data_cube = xr.concat([self.data_cube, new_data], dim="region", combine_attrs="override")

    def geometry_iterator(self) -> (str, ee.Geometry):
        """
        Generator that iterates through the geometries in the shapefile
        @return: a tuple of the region name and the geometry
        """
        for index, row in self.shp.iterrows():
            region_name = row[self.region_col]
            geometry = ee.Geometry.Polygon(list(row['geometry'].exterior.coords))
            yield region_name, geometry

    def date_iterator(self) -> ee.Date:
        """
        Generator that iterates through the dates between the start and end dates
        @return: an ee.Date object
        """
        start_date = datetime.strptime(self.s_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.e_date, "%Y-%m-%d")
        for n in range(int((end_date - start_date).days)):
            yield ee.Date(start_date + timedelta(n))

    def safe_netcdf(self):
        """
        Save the data cube to a netcdf file.
        """
        self.data_cube.to_netcdf(f"modis_lst_data_cube.nc")

    def create_data_cube(self):
        for region_name, geometry in self.geometry_iterator():
            for date in self.date_iterator():
                tmax, tmin = self.get_extreme_temperature_data_area_date(geometry, date)
                self.append_to_data_cube(region_name, date, tmax.getInfo(), tmin.getInfo())

    def query(self,
              region_name: str,
              date: str) -> (float, float):
        """
        Get the min and max temperature for a given region and date
        @param region_name: the name of the region
        @param date: the date of the data
        @return: a tuple of the max and min temperature
        """
        date = datetime.strptime(date, "%Y-%m-%d")
        result = self.data_cube.loc[(self.data_cube['region'] == region_name) & (self.data_cube['Date'] == date)]
        return result[['tmax', 'tmin']]


obj = ModisLST('boundary_data/sa2_nsw.shp', '2021-01-01', '2021-2-1', 'SA1_MAIN16')
obj.create_data_cube()
print(obj.query('10602111401', '2021-1-15'))
