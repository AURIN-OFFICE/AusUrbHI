import csv
import warnings
import geopandas as gpd

warnings.filterwarnings('ignore', '.*Column names longer than 10 characters will be '
                                  'truncated when saved to ESRI Shapefile.*')


class Cleanser:
    def __init__(self, data_path):
        self.data_name = data_path.split('\\')[-1].split('.')[0]
        self.data = gpd.read_file(data_path)

    def refine_by_study_area(self,
                             year,
                             output_dir,
                             study_area_matching_column=None,
                             data_matching_column=None):
        """refine data by study area boundary shapefile"""

        # decide which study area to use
        if year == 2016:
            study_area_path = "..\\_data\\study area\\sa1_nsw.shp"
            study_area_matching_column = "SA1_MAIN16" if not study_area_matching_column else study_area_matching_column
            data_matching_column = "sa1_main16" if not data_matching_column else data_matching_column
        elif year == 2021:
            study_area_path = "..\\_data\\study area\\ausurbhi_study_area_2021.shp"
            study_area_matching_column = "SA1_CODE21" if not study_area_matching_column else study_area_matching_column
            data_matching_column = "SA1_CODE_2" if not data_matching_column else data_matching_column
        else:
            raise ValueError("Year must be either 2016 or 2021.")

        # validate data matching column is in data
        assert data_matching_column in self.data.columns

        # validate study area matching column is in study area
        study_area_data = gpd.read_file(study_area_path)
        assert study_area_matching_column in study_area_data.columns

        # validate all values in the study area matching column are present in the data matching column
        if not study_area_data[study_area_matching_column].isin(self.data[data_matching_column]).all():
            print(f"WARNING: Not all values from {study_area_matching_column} are present in {data_matching_column}.")

        # refine data
        refined_data = self.data[self.data[data_matching_column].astype(str).isin(
            study_area_data[study_area_matching_column].astype(str))]

        # rename the data_matching_column to study_area_matching_column
        refined_data = refined_data.rename(columns={data_matching_column: study_area_matching_column})

        # save refined data
        output_path = output_dir + self.data_name + "_study_area_refined.shp"
        refined_data.to_file(output_path)

    def refine_attribute(self):
        pass

    def convert_to_sa1(self):
        pass

    def convert_to_2021_study_area(self,
                                   correspondence_file_path="..\\_data\\study area\\CG_SA1_2016_SA1_2021.csv"):
        with open(correspondence_file_path, 'r') as f:
            correspondence_file = csv.reader(f)

    def normalization(self):
        pass
