import pandas as pd
import geopandas as gpd
from tqdm import tqdm


class ConcordanceMapper:
    def __init__(self, filename=None):
        self.pha_2_sa2_dict = None
        self.sa2_2_sa1_dict = None
        self.filename = filename

    def create_pha_has_number_of_sa2_dict(self):
        csv_path = "../_data/study area/PHIDU_2016_SA2_PHA.csv"
        csv_data = pd.read_csv(csv_path)

        # Initialize an empty dictionary
        pha_2_sa2_dict = {}

        # Loop through each row in the DataFrame
        for index, row in csv_data.iterrows():
            pha_code = row['PHA code']
            sa2_code = row['SA2 code']

            # If PHA code is not already in dictionary, initialize with 0
            if pha_code not in pha_2_sa2_dict:
                pha_2_sa2_dict[pha_code] = 0

            # Increment count for this PHA code by 1 (corresponding to one SA2 code)
            pha_2_sa2_dict[pha_code] += 1

        self.pha_2_sa2_dict = pha_2_sa2_dict

    def create_sa2_has_number_of_sa1_dict(self):
        shp_path = "../_data/study area/ausurbhi_study_area_2021.shp"
        gdf = gpd.read_file(shp_path)

        # Initialize an empty dictionary to store the counts
        sa2_to_sa1_dict = {}

        # Loop through each row in the GeoDataFrame
        for index, row in gdf.iterrows():
            sa1_code = row['SA1_CODE21']
            sa2_code = row['SA2_CODE21']

            # Update the dictionary count
            if sa2_code in sa2_to_sa1_dict:
                sa2_to_sa1_dict[sa2_code] += 1
            else:
                sa2_to_sa1_dict[sa2_code] = 1

        self.sa2_2_sa1_dict = sa2_to_sa1_dict

    def divide_pha_data_by_number_of_sa2(self, gdf, exclude_division_field_list):
        """Divide pha data value by number of sa2s in pha. GDF is already at sa2 level."""
        new_gdf = gdf.copy()

        # Loop through each row in the GeoDataFrame
        for idx, row in tqdm(new_gdf.iterrows(), total=len(new_gdf), desc=f"PHA to SA2 for {self.filename}"):

            # Get the PHA code for the current row
            pha_code = int(row['pha_code'])

            # assert code is in the dictionary
            assert pha_code in self.pha_2_sa2_dict, f"pha_code {pha_code} not in pha_2_sa2_dict"

            # Get the number of SA2s for this PHA code from the dictionary
            num_sa2s = self.pha_2_sa2_dict.get(pha_code)

            # Loop through each field in the GeoDataFrame
            for field in new_gdf.columns:

                # Skip the fields that should not be divided
                if field in exclude_division_field_list:
                    continue

                # Divide the field value by the number of SA2s
                try:
                    new_gdf.at[idx, field] = round(float(row[field]) / num_sa2s, 2)
                except ValueError:
                    if all(sub not in str(row[field]) for sub in ['~', '**', 'nan']):
                        print(f"ValueError: {row[field]} from {pha_code}:{field} is not a number")

        # Remove duplicate entries
        new_gdf = new_gdf.drop_duplicates()

        return new_gdf

    def convert_sa2_to_sa1_and_divide(self, sa2_gdf, study_area_gdf, exclude_division_field_list):
        """convert sa2 shp to sa1 and divide data value by number of sa1s in sa2"""
        # Perform a join between study_area_gdf and sa2_gdf based on 'SA2_CODE21'
        merged_gdf = pd.merge(study_area_gdf, sa2_gdf, on="SA2_CODE21", how="left", suffixes=('_sa1', '_sa2'))

        # Create an empty list to store the columns that need to be divided
        columns_to_divide = []

        # Loop through the columns to identify which ones should be divided
        for column in sa2_gdf.columns:
            if column not in exclude_division_field_list and column != 'SA2_CODE21' and column != 'geometry':
                columns_to_divide.append(column)

        # Loop through the rows to perform the division based on sa2_to_sa1_dict

        for index, row in tqdm(merged_gdf.iterrows(), total=len(merged_gdf), desc=f"SA2 to SA1 for {self.filename}"):
            sa2_code = row['SA2_CODE21']
            divisor = self.sa2_2_sa1_dict.get(sa2_code, 1)  # Get the divisor, if not found then use 1
            for column in columns_to_divide:
                if pd.notnull(row[column]):
                    merged_gdf.at[index, column] = round(float(row[column]) / divisor, 2)

        # Drop unwanted columns that are duplicated during the merge operation
        for column in merged_gdf.columns:
            if column.endswith('_sa1'):
                merged_gdf.drop(columns=[column], inplace=True)

        # Create a new GeoDataFrame
        new_gdf = gpd.GeoDataFrame(merged_gdf, geometry='geometry')

        # Save the GeoDataFrame as a new shapefile
        new_gdf.to_file("new_shapefile.shp")

        return new_gdf
