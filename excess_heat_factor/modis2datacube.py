# -*- coding: utf-8 -*-
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

import ee
import geopandas as gpd
import pandas as pd


class ModisLST:
    """
    This class is used to get the maximum and minimum temperature of a region from MODIS LST data.
    """
    def __init__(self,
                 boundary_shapefile: str,
                 region_shapefile: str,
                 shp_region_column: str,
                 start_date: str,
                 end_date: str):
        """
        @param boundary_shapefile: the shapefile of the boundary of the study area.
        @param region_shapefile: the shapefile of the regions of the study area.
        @param shp_region_column: the column name of the region name in the shapefile.
        @param start_date: the start date of the data.
        @param end_date: the end date of the data.
        """

        # ee.Authenticate()
        ee.Initialize()

        # get the boundary of the study area
        gdf = gpd.read_file(boundary_shapefile)
        bounding_box = gdf.geometry.iloc[0].bounds
        self.boundary = self.bounding_box_to_ee_multipolygon(bounding_box)

        # get the regions of the study area
        self.gdf = gpd.read_file(region_shapefile)

        # get the column name of the region name
        self.region_col = shp_region_column

        # get the start and end date
        self.s_date = start_date
        self.e_date = end_date

        # initiate an empty dict to store the maximum and minimum temperature of each region
        self.dict_data = defaultdict(lambda: defaultdict(dict))

    @staticmethod
    def bounding_box_to_ee_multipolygon(bbox: tuple) -> ee.Geometry.MultiPolygon:
        """
        Convert a bounding box to an ee.Geometry.MultiPolygon.
        @param bbox:
        @return: an ee.Geometry.MultiPolygon
        """
        coordinates = [
            [
                [bbox[0], bbox[1]],
                [bbox[0], bbox[3]],
                [bbox[2], bbox[3]],
                [bbox[2], bbox[1]],
                [bbox[0], bbox[1]]
            ]
        ]
        return ee.Geometry.MultiPolygon(coordinates)

    def geometry_iterator(self) -> (str, ee.Geometry):
        """
        Iterate over the regions of the study area.
        @return: a tuple of the region name and the ee.Geometry of the region.
        """
        for index, row in self.gdf.iterrows():
            region_name = row[self.region_col]
            try:
                geometry = list(row['geometry'].exterior.coords)
            except AttributeError:
                # if the geometry is a multipolygon
                # print(f"info: region {region_name} contains multipolygon.")
                geometry = list(row['geometry'].convex_hull.exterior.coords)
            yield str(region_name), ee.Geometry.Polygon(geometry)

    def get_max_min_temperature(self):
        """
        Calculate the maximum and minimum temperature of each region.
        """
        def convert_celsius(image: ee.Image):
            """
            Convert the temperature from Kelvin to Celsius.
            @param image: an ee.Image
            @return: an ee.Image
            """
            return image\
                .multiply(0.02)\
                .subtract(273.15)\
                .select(['LST_Day_1km', 'LST_Night_1km'])

        # get the maximum and minimum temperature image collection
        modis = ee\
            .ImageCollection("MODIS/006/MOD11A1")\
            .filterDate(self.s_date, self.e_date)\
            .filterBounds(self.boundary) \
            .map(convert_celsius)

        # get the maximum and minimum temperature of each region
        count = 1
        total = len(self.gdf)
        for region_name, geometry in self.geometry_iterator():
            def calculate_daily_min_max(image: ee.Image) -> ee.Feature:
                """
                Calculate the maximum and minimum temperature of each day.
                @param image: an ee.Image
                @return: an ee.Feature
                """
                daily_min_max = image.reduceRegion(
                    reducer=ee.Reducer.minMax(),
                    geometry=geometry
                )
                return ee.Feature(None, daily_min_max)

            # get the maximum and minimum temperature of each day
            daily_min_max_features = modis.map(calculate_daily_min_max)

            # populate data dictionary
            for row in daily_min_max_features.getInfo()['features']:
                tmax = row['properties']['LST_Day_1km_max']
                tmin = row['properties']['LST_Night_1km_min']
                self.dict_data[region_name][row["id"]]["tmax"] = tmax
                self.dict_data[region_name][row["id"]]["tmin"] = tmin
            print(f"region {region_name} temperature info obtained, {round(count*100/total, 1)}%.")
            count += 1

    def get_geometry(self, region):
        """
        Get the geometry of a region.
        @param region: the name of the region.
        @return: an ee.Geometry
        """
        row = self.gdf.loc[self.gdf[self.region_col] == region]
        if not row.empty:
            return row['geometry'].iloc[0]
        else:
            print(f"warning: no geometry data found for region: {region}")
            return None

    def save_json(self,
                  json_filedir: str,
                  netcdf_dir: str):
        """
        Save the data to a json file and a netcdf data cube file.
        @param json_filedir: the directory of the json file.
        @param netcdf_dir: the directory of the netcdf data cube file.
        """
        if not os.path.exists(json_filedir):
            with open(json_filedir, "w") as outfile:
                json.dump(self.dict_data, outfile)

        # Prepare the data for xarray
        data = {
            "tmax": [],
            "tmin": []
        }
        index_data = {
            "region": [],
            "date": [],
            "geometry": []
        }

        # Load temperature json data
        if self.dict_data:
            dict_data = self.dict_data
        else:
            with open(json_filedir, 'r') as f:
                dict_data = json.load(f)

        # Populate the data cube
        count = 0
        total = len(dict_data.keys())
        index_data = {"region": [], "date": [], "geometry": []}
        for region, date_dict in dict_data.items():
            for date, temp_data in date_dict.items():
                index_data["region"].append(region)
                date = datetime.strptime(date, '%Y_%m_%d')
                index_data["date"].append(pd.to_datetime(date))
                data["tmax"].append(temp_data["tmax"])
                data["tmin"].append(temp_data["tmin"])
                # geometry = self.get_geometry(region)
                # index_data["geometry"].append(geometry)
            print(f"region {region} added to data cube, {round(count * 100 / total, 1)}%.")
            count += 1

        # Create a multi-indexed pandas DataFrame
        multi_index = pd.MultiIndex.from_tuples(
            list(zip(index_data["region"], index_data["date"])), names=["region", "date"]
        )

        df = pd.DataFrame(data, index=multi_index)

        # Convert the DataFrame to a GeoDataFrame
        # gdf = gpd.GeoDataFrame(df, geometry=index_data["geometry"])

        # Convert the GeoDataFrame to a xarray Dataset
        ds = df.to_xarray()

        # Save the xarray Dataset as a NetCDF file
        ds.to_netcdf(netcdf_dir)

    @staticmethod
    def query(filedir: str,
              region_name: str,
              date: str):
        """
        Query the maximum and minimum temperature of a region on a specific date.
        @param filedir: the directory of the json file.
        @param region_name: the name of the region.
        @param date: the date.
        """
        with open(filedir, 'r') as f:
            data = json.load(f)
        tmax = data[region_name][date]["tmax"]
        tmin = data[region_name][date]["tmin"]
        print(tmax, tmin)


if __name__ == '__main__':
    json_dir = "modis_lst_data.json"
    obj = ModisLST('boundary_data/boundaries.shp', 'boundary_data/sa3_nsw.shp',
                   'SA3_CODE16', '2019-12-01', '2020-03-01')
    if not os.path.exists(json_dir):
        obj.get_max_min_temperature()
    obj.save_json(json_dir, "modis_lst_data_cube.nc")
    # obj.query("modis_lst_data.json", '106021114', '2020-1-15')
