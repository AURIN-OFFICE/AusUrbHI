# -*- coding: utf-8 -*-

import ee
import geopandas as gpd
import pandas as pd
import xarray as xr
from shapely.geometry import Polygon, MultiPolygon
from tqdm import tqdm


class ModisDataProcessor:
    def __init__(self, product, region_collection_shp, geo_level_column, start_date, end_date, scale):
        # ee.Authenticate()
        ee.Initialize()

        self.product = product
        self.region_collection_gdf = gpd.read_file(region_collection_shp)[:1]
        self.study_area = self.compute_study_area()
        self.geo_level_column = geo_level_column
        self.start_date = start_date
        self.end_date = end_date
        self.scale = scale
        self.data = []

    def compute_study_area(self):
        minx, miny, maxx, maxy = self.region_collection_gdf.total_bounds
        coords = [[minx, miny], [minx, maxy], [maxx, maxy], [maxx, miny], [minx, miny]]
        bounding_box = ee.Geometry.Polygon(coords)
        return bounding_box

    @staticmethod
    def shapely_to_ee(geom):
        geojson = geom.__geo_interface__
        if isinstance(geom, Polygon):
            return ee.Geometry.Polygon(geojson['coordinates'])
        elif isinstance(geom, MultiPolygon):
            return ee.Geometry.MultiPolygon(geojson['coordinates'])

    @staticmethod
    def convert_to_celsius(image):
        return image.select(['LST_Day_1km', 'LST_Night_1km']).multiply(0.02).subtract(273.15)

    def fetch_data(self):
        image_collection = ee\
            .ImageCollection(self.product)\
            .filterDate(self.start_date, self.end_date)\
            .filterBounds(self.study_area) \
            .map(self.convert_to_celsius)

        for _, row in tqdm(self.region_collection_gdf.iterrows(),
                           total=self.region_collection_gdf.shape[0],
                           desc=f"Iterating over regions from {self.geo_level_column}"):
            region_id = row[self.geo_level_column]
            geom = self.shapely_to_ee(row['geometry'])
            data = image_collection.getRegion(geom, self.scale).getInfo()
            df = pd.DataFrame(data)
            print(df)

    def save_shapefile(self, file_name):
        flat_data = [item for sublist in self.data for item in sublist]
        df = pd.DataFrame(flat_data)
        df.set_index('region_id', inplace=True)

        reshaped_df = pd.DataFrame()
        for date_col in df.columns:
            date = pd.to_datetime(date_col)
            day_max_col = f"{date_col}_DayMax"
            night_min_col = f"{date_col}_NightMin"
            reshaped_df[day_max_col] = df[date_col].apply(lambda x: x.get('LST_Day_1km'))
            reshaped_df[night_min_col] = df[date_col].apply(lambda x: x.get('LST_Night_1km'))

        gdf = self.region_collection_gdf[[self.geo_level_column, 'geometry']].\
            merge(reshaped_df, left_on=self.geo_level_column, right_index=True)
        gdf.to_file(file_name, driver='ESRI Shapefile')

    def save_netcdf(self, file_name):
        flat_data = [item for sublist in self.data for item in sublist]
        df = pd.DataFrame(flat_data)
        df.set_index('region_id', inplace=True)
        xds = xr.Dataset.from_dataframe(df)
        xds.to_netcdf(file_name)


if __name__ == '__main__':
    product = "MODIS/006/MOD11A1"
    region_collection_shp = "../_data/boundary_data/sa4_nsw.shp"
    geo_level_column = "SA4_CODE16"
    start_date = "2020-01-02"
    end_date = "2020-01-06"
    scale = 500
    shapefile_name = f"{geo_level_column}_{start_date}_{end_date}.shapefile"
    netcdf_name = f"{geo_level_column}_{start_date}_{end_date}.nc"

    processor = ModisDataProcessor(product, region_collection_shp, geo_level_column,
                                   start_date, end_date, scale)
    processor.fetch_data()
    # processor.save_shapefile(shapefile_name)
    # processor.save_netcdf(netcdf_name)
