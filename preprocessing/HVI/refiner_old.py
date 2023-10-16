# -*- coding: utf-8 -*-
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


class RefineStudyArea:
    def __init__(self,
                 study_area_file: str,
                 study_area_matching_column: str,
                 data_file: str,
                 data_area_matching_column: str):
        self.study_area = gpd.read_file(study_area_file)
        self.study_area_matching_column = study_area_matching_column
        self.data = gpd.read_file(data_file)
        self.data_area_matching_column = data_area_matching_column

    def inspect_data(self):
        fig1, ax1 = plt.subplots(figsize=(20, 20))
        self.study_area.plot(ax=ax1)
        ax1.set_title("Study Area")
        plt.show()

        print(self.study_area.head())

        fig2, ax2 = plt.subplots(figsize=(20, 20))
        self.data.plot(ax=ax2)
        ax2.set_title("Data")
        plt.show()

        print(self.data.head())

    def refine_data(self):
        self.refined_data = self.data[self.data[self.data_area_matching_column]
        .isin(self.study_area[study_area_matching_column])]

    def plot_refined_data(self):
        self.refined_data.plot(figsize=(20, 20))
        plt.title("Refined Data")
        plt.show()

    def save_refined_data(self, output_file):
        self.refined_data.to_file(output_file)


if __name__ == "__main__":
    study_area_file = "../../_data/study_area/sa1_nsw.shp"
    study_area_matching_column = "SA1_MAIN16"
    data_file = "../../_data/study_area/datasource-AU_Govt_ABS-UoM_AURIN_DB_3_seifa_ieo_aust_sa1_2011.json"
    data_area_matching_column = "sa1_code"
    output_file = f"refined_{data_file.split('/')[-1].split('.')[0]}.shp"
    inspect = True

    refiner = RefineStudyArea(study_area_file,
                            study_area_matching_column,
                            data_file,
                            data_area_matching_column)
    print("data loaded.")
    if inspect:
        refiner.inspect_data()
    print("start refining data.")
    refiner.refine_data()
    if inspect:
        refiner.plot_refined_data()
    refiner.save_refined_data(output_file)
    print("refined data saved.")
