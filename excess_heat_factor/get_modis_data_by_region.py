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
        self.geo_level_column = geo_level_column
        self.study_area = ee.Geometry.Polygon([list(self.region_collection_gdf['geometry'][0].exterior.coords)])
        self.region_collection_ee_feature = self.convert_feature()
        self.start_date = start_date
        self.end_date = end_date
        self.scale = scale

    def create_feature(self, polygon, row):
        """
        Create a feature with given polygon and row data.

        Args:
        polygon (geometry): Polygon geometry.
        row (dataframe row): A row of data.

        Returns:
        feature: A feature created with given polygon and data.
        """
        # Convert the polygon to an ee.Geometry object
        polygon = ee.Geometry.Polygon(list(polygon.exterior.coords))

        # Create a feature with the polygon and data
        feature = ee.Feature(polygon, {self.geo_level_column: row[self.geo_level_column]})

        return feature

    def convert_feature(self):
        """
        Convert the regions in region_collection_gdf to features.

        Returns:
        featureCollection: A FeatureCollection of converted features.
        """
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

        # Create a FeatureCollection with the list of features
        self.region_collection_feature = ee.FeatureCollection(feature_list)

        return self.region_collection_feature

    @staticmethod
    def convert_to_celsius(image):
        """
        Convert image to Celsius scale.

        Args:
        image (ee.Image): Image to convert.

        Returns:
        image: Converted image.
        """
        # Convert to Celsius
        return image.select(['LST_Day_1km', 'LST_Night_1km']).multiply(0.02).subtract(273.15)

    def fetch_data(self):
        """
        Fetch MODIS LST data for the given study area and date range.
        """
        # Create an ImageCollection for MODIS LST data
        self.image_collection = ee \
            .ImageCollection("MODIS/006/MOD11A2") \
            .filterDate(self.start_date, self.end_date) \
            .filterBounds(self.study_area) \
            .map(self.convert_to_celsius)

    def reduce_region(self, image):
        """
        Reduce the image to regions.

        Args:
        image (ee.Image): Image to reduce.

        Returns:
        reduced_image: Reduced image.
        """
        # Reduce the image to the regions
        reduced_image = image.reduceRegions(self.region_collection_feature, ee.Reducer.minMax(), self.scale)

        return reduced_image

    def process_data(self):
        """
        Process the fetched MODIS LST data.
        """
        # Convert start and end dates to datetime objects
        self.start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(self.end_date, '%Y-%m-%d')

        # Calculate the date range
        delta = self.end_date - self.start_date

        result = []

        # Process data day by day to avoid large payload size
        for i in tqdm(range(delta.days + 1), desc="Processing data"):
            # Calculate the date for the current day
            day = self.start_date + timedelta(days=i)

            # Filter the data for the current day
            day_collection = self.image_collection.filter(ee.Filter.calendarRange(day.day, day.day, 'day_of_year'))

            # Reduce the data to the regions
            daily_data = day_collection.map(self.reduce_region)

            # Fetch data for each day individually
            daily_data_info = daily_data.getInfo()
            result.append(daily_data_info)

        # Store the result
        self.data = result

    def save_as_netcdf(self, file_name):
        """
        Save the processed data as a netCDF file.

        Args:
        file_name (str): Name of the netCDF file.
        """
        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(self.data)

        # Convert the DataFrame to an xarray Dataset
        xds = xr.Dataset.from_dataframe(df)

        # Save the Dataset as a netCDF file
        xds.to_netcdf(file_name)


if __name__ == '__main__':
    def main():
        region_collection_shp = "../_data/boundary_data/sa2_nsw.shp"
        geo_level_column = "SA2_MAIN16"
        start_date = "2019-07-01"
        end_date = "2019-07-05"
        scale = 100
        save_file_name = "modis_data.nc"

        processor = ModisDataProcessor(region_collection_shp, geo_level_column, start_date, end_date, scale)
        processor.fetch_data()
        processor.process_data()
        processor.save_as_netcdf(save_file_name)

    main()
