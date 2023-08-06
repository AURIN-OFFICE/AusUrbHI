import csv
import warnings
import geopandas as gpd
from .phidu_short_field_name_dict import phidu_short_field_name_dict

warnings.filterwarnings('ignore', '.*Column names longer than 10 characters will be '
                                  'truncated when saved to ESRI Shapefile.*')


class Cleanser:
    def __init__(self, data_path):
        self.data_name = data_path.split('\\')[-1].split('.')[0]
        self.data = gpd.read_file(data_path)

    def refine_by_study_area(self,
                             year,
                             output_dir,
                             study_area_matching_column,
                             data_matching_column):
        """refine data by study area boundary shapefile"""

        # decide which study area to use
        if year == "2016":
            study_area_path = "..\\_data\\study area\\ausurbhi_study_area_2016_with_pha.shp"
        elif year == "2021":
            study_area_path = "..\\_data\\study area\\ausurbhi_study_area_2021.shp"
        else:
            raise ValueError("Year must be either 2016 or 2021.")

        # validate data matching column is in data
        assert data_matching_column in self.data.columns

        # validate study area matching column is in study area
        study_area_data = gpd.read_file(study_area_path)
        assert study_area_matching_column in study_area_data.columns

        # warn if not all values in the study area matching column are present in the data matching column
        if not study_area_data[study_area_matching_column].isin(self.data[data_matching_column]).all():
            print(f"Data Gap Warning: Not all values from {study_area_matching_column} "
                  f"are present in {data_matching_column}.")

        # refine data
        refined_data = self.data[self.data[data_matching_column].astype(str).isin(
            study_area_data[study_area_matching_column].astype(str))]

        # rename the data_matching_column to study_area_matching_column
        refined_data = refined_data.rename(columns={data_matching_column: study_area_matching_column})

        # shorten column names and add SA2 codes to the resulting shapefile
        if data_matching_column == "pha_code":
            refined_data.columns = [phidu_short_field_name_dict[col] if col in phidu_short_field_name_dict
                                    else col for col in refined_data.columns]

            # Convert the study_area_matching_column in both dataframes to the same type
            refined_data[study_area_matching_column] = refined_data[study_area_matching_column].astype(str)
            study_area_data[study_area_matching_column] = study_area_data[study_area_matching_column].astype(str)

            # merge the refined data with the study area data to get the "SA2_MAIN16" attribute
            refined_data = refined_data.merge(study_area_data[[study_area_matching_column, "SA2_MAIN16"]],
                                              on=study_area_matching_column, how='left')

        # save refined data
        output_path = output_dir + self.data_name + "_study_area_refined.shp"
        refined_data.to_file(output_path)

    def refine_attribute(self):
        pass

    def pha_to_sa2(self):
        pass

    def sa2_to_sa1(self):
        pass

    def convert_2016_sa1_to_2021(self, correspondence_file_path="..\\_data\\study area\\CG_SA1_2016_SA1_2021.csv"):
        with open(correspondence_file_path, 'r') as f:
            correspondence_file = csv.reader(f)

    def normalization(self):
        pass
