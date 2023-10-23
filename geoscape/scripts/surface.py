import os
import geopandas as gpd
from osgeo import gdal, ogr


class LandUseAnalysis:
    def __init__(self, tif_directory, study_area_path):
        self.tif_directory = tif_directory
        self.study_area_path = study_area_path
        self.sa1_shapefile = gpd.read_file(self.study_area_path)

    def rasterize_vector(self, output_path, raster_ex, value=1):
        ref_raster = gdal.Open(raster_ex)
        x_res, y_res = ref_raster.RasterXSize, ref_raster.RasterYSize
        geo_transform = ref_raster.GetGeoTransform()
        proj = ref_raster.GetProjectionRef()

        target_ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, 1, gdal.GDT_Byte)
        target_ds.SetGeoTransform(geo_transform)
        target_ds.SetProjection(proj)

        options = ['ATTRIBUTE=' + str(value)]
        gdal.RasterizeLayer(target_ds, [1], ogr.Open(self.study_area_path).GetLayer(0), options=options)

        gdal.GetDriverByName('GTiff').CreateCopy(output_path, target_ds)

    def calculate_area_percentage(self, landuse_raster, sa1_rasterized, landuse_value):
        lu_raster = gdal.Open(landuse_raster)
        sa1_raster = gdal.Open(sa1_rasterized)

        lu_band = lu_raster.GetRasterBand(1)
        sa1_band = sa1_raster.GetRasterBand(1)

        lu_data = lu_band.ReadAsArray()
        sa1_data = sa1_band.ReadAsArray()

        intersection = (lu_data == landuse_value) & (sa1_data == 1)

        total_sa1 = (sa1_data == 1).sum()
        intersect_sum = intersection.sum()

        return (intersect_sum / total_sa1) * 100

    def process_all_rasters(self):
        results = {}
        for file in os.listdir(self.tif_directory):
            if file.endswith('.tif'):
                raster_path = os.path.join(self.tif_directory, file)
                rasterized_sa1_path = os.path.join(self.tif_directory, f"rasterized_{file}")

                self.rasterize_vector(rasterized_sa1_path, raster_path)

                # You'd have to determine how your landuse values are defined.
                # Here's a simple example assuming values are 1, 2, and 3.
                percentages = {}
                for landuse_value in [1, 2, 3]:
                    percentages[landuse_value] = self.calculate_area_percentage(raster_path, rasterized_sa1_path, landuse_value)

                results[file] = percentages

        return results


# File paths:
tif_folder_path = "../../_data/AusUrbHI HVI data unprocessed/Geoscape/temporary/surface_tif"
study_area_path = "../../_data/study area/ausurbhi_study_area_2021.shp"

# Example of using the class:
analysis = LandUseAnalysis(tif_folder_path, study_area_path)
analysis.process_all_rasters()

