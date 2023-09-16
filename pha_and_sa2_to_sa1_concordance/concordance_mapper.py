import pandas as pd
import geopandas as gpd
from tqdm import tqdm


class ConcordanceMapper:
    def __init__(self):
        self.pha_2_sa2_dict = None
        self.sa2_2_sa1_dict = None

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

    def divide_pha_data_by_number_of_sa2(self, gdf, exclude_division_field_list, filename):
        """Divide pha data value by number of sa2s in pha. GDF is already at sa2 level."""
        new_gdf = gdf.copy()

        # Loop through each row in the GeoDataFrame
        for idx, row in tqdm(new_gdf.iterrows(),
                             total=len(new_gdf),
                             desc=f"processing {filename}",
                             position=1,
                             leave=False):

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
                if row[field] is not None:
                    new_gdf.at[idx, field] = float(row[field]) / num_sa2s

        return new_gdf

    def convert_sa2_shp_to_sa1(self):
        """convert sa2 shp to sa1"""

        return

    def divide_sa2_data_by_number_of_sa1(self):
        """Divide sa2 data value by number of sa1s in sa2. gdf is already at sa1 level."""

        return
