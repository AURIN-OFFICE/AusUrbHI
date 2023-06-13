# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import ee
import geopandas as gpd
import pandas as pd
import xarray as xr
from tqdm import tqdm


class ModisDataProcessor:
    def __init__(self, region_collection_shp, geo_level_column, start_date, end_date, scale):
        ee.Initialize()

        self.region_collection_gdf = gpd.read_file(region_collection_shp)
        self.study_area = self.compute_study_area()
        self.geo_level_column = geo_level_column
        self.region_collection_ee_feature = self.convert_ee_feature()
        self.start_date = start_date
        self.end_date = end_date
        self.scale = scale

    def compute_study_area(self):
        """Compute the minimum bounding box of the region collection as an ee Polygon."""
        minx, miny, maxx, maxy = self.region_collection_gdf.total_bounds
        coords = [[minx, miny], [minx, maxy], [maxx, maxy], [maxx, miny], [minx, miny]]
        bounding_box = ee.Geometry.Polygon(coords)
        return bounding_box

    def create_feature(self, polygon, row):
        polygon = ee.Geometry.Polygon(list(polygon.exterior.coords))
        feature = ee.Feature(polygon, {self.geo_level_column: row[self.geo_level_column]})
        return feature

    def convert_ee_feature(self):
        """Convert the regions in region_collection_gdf to a list of ee features."""
        feature_list = []
        for _, row in self.region_collection_gdf.iterrows():
            geom = row['geometry']

            # Check if the geometry is a MultiPolygon
            if geom.geom_type == 'MultiPolygon':
                for polygon in geom.geoms:
                    feature = self.create_feature(polygon, row)
                    feature_list.append(feature)
            else:  # It's a normal Polygon
                feature = self.create_feature(geom, row)
                feature_list.append(feature)

        return ee.FeatureCollection(feature_list)

    @staticmethod
    def convert_to_celsius(image):
        return image.select(['LST_Day_1km', 'LST_Night_1km']).multiply(0.02).subtract(273.15)

    def reduce_region(self, image):
        return image.reduceRegion(self.region_collection_ee_feature, ee.Reducer.minMax(), self.scale)

    def fetch_data(self):
        image_collection = ee \
            .ImageCollection("MODIS/006/MOD11A2") \
            .filterDate(self.start_date, self.end_date) \
            .filterBounds(self.study_area) \
            .map(self.convert_to_celsius) \
            .select(['LST_Day_1km', 'LST_Night_1km'])

        self.start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
        delta = self.end_date - self.start_date


        # Process data day by day to avoid large payload size
        for i in tqdm(range(delta.days + 1):
            # Calculate the date for the current day
            day = self.start_date + timedelta(days=i)

            # Filter the data for the current day
            day_collection = image_collection.filter(ee.Filter.calendarRange(day.day, day.day, 'day_of_year'))

            # Reduce the data to the regions
            daily_data = day_collection.map(self.reduce_region)

            # Fetch data for each day individually
            daily_data_info = daily_data.getInfo()
            result.append(daily_data_info)


if __name__ == '__main__':
    def main():
        region_collection_shp = "../_data/boundary_data/sa4_nsw.shp"
        geo_level_column = "SA4_CODE16"
        start_date = "2019-07-01"
        end_date = "2019-07-05"
        scale = 100
        save_file_name = "modis_data.nc"

        processor = ModisDataProcessor(region_collection_shp, geo_level_column, start_date, end_date, scale)
        processor.fetch_data()
        processor.save_as_netcdf(save_file_name)

    main()
