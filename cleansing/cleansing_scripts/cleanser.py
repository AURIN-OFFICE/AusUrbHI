import csv
import geopandas as gpd


class Cleanser:
    def __init__(self, data_path):
        self.data_name = data_path.split('/')[-1].split('.')[0]
        self.data = gpd.read_file(data_path)

    def refine_by_study_area(self, year, output_dir):
        """refine data by study area boundary shapefile"""

        # decide which study area to use
        if year == 2016:
            study_area_path = "../_data/study area/sa1_nsw.shp"
            study_area_matching_column = "SA1_MAIN16"
            data_matching_column = "sa1_main16"
        elif year == 2021:
            study_area_path = "../_data/study area/ausurbhi_study_area_2021.shp"
            study_area_matching_column = "SA1_CODE21"
            data_matching_column = "SA1_CODE_2"
        else:
            raise ValueError("Year must be either 2016 or 2021.")

        # validate data matching column is in data
        assert data_matching_column in self.data.columns

        # validate study area matching column is in study area
        study_area_data = gpd.read_file(study_area_path)
        assert study_area_matching_column in study_area_data.columns

        # validate all values in the study area matching column are present in the data matching column
        assert study_area_data[study_area_matching_column].isin(self.data[data_matching_column]).all(), \
            f"Not all values from {study_area_matching_column} are present in {data_matching_column}."

        # refine data
        refined_data = self.data[self.data[data_matching_column].isin(study_area_data[study_area_matching_column])]

        # save refined data
        output_name = self.data_name + "_study_area_refined.shp"
        output_path = output_dir + output_name if output_dir[-1] == "/" else output_dir + "/" + output_name
        refined_data.to_file(output_path)

    def convert_to_shapefile(self):
        pass

    def refine_attribute(self):
        pass

    def convert_to_2021_study_area(self,
                                   correspondence_file_path="../_data/study area/CG_SA1_2016_SA1_2021.csv"):
        with open(correspondence_file_path, 'r') as f:
            correspondence_file = csv.reader(f)
