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
            sa2_code = row['SA2_CODE21']

            # Update the dictionary count
            if sa2_code in sa2_to_sa1_dict:
                sa2_to_sa1_dict[sa2_code] += 1
            else:
                sa2_to_sa1_dict[sa2_code] = 1

        self.sa2_2_sa1_dict = sa2_to_sa1_dict

    @staticmethod
    def divide_value(value, divisor, code, column):
        """Divide the field value by the number of SA2s/SA1s in PHA/SA2."""
        try:
            value = float(str(value).replace(",", ""))
            return round(value / divisor, 2)
        except ValueError:
            if all(sub not in str(value) for sub in ['~', '-', '**', '*', 'nan']):
                tqdm.write(f"ValueError: {value} from {code}:{column} is not a number")
            return value

    def divide_pha_data_by_number_of_sa2(self, gdf, exclude_division_field_list):
        """Divide pha data value by number of SA2s in pha. GDF is already at sa2 level."""
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
                if field in exclude_division_field_list + ['INDIV_QLTY', 'OVR_QLTY']:
                    continue

                # Divide the field value by the number of SA2s
                new_gdf.at[idx, field] = self.divide_value(row[field], num_sa2s, pha_code, field)

        # Remove duplicate entries
        new_gdf = new_gdf.drop_duplicates()

        return new_gdf

    def convert_sa2_to_sa1_and_divide(self, sa2_gdf, study_area_gdf, exclude_division_field_list):
        """Convert sa2 shp to sa1 and divide data value by number of sa1s in sa2."""

        # Initialize an empty list to hold rows for the new GeoDataFrame
        new_rows = []

        # Loop through each row in study_area_gdf
        for index, row in tqdm(study_area_gdf.iterrows(), total=len(study_area_gdf),
                               desc=f"SA2 to SA1 for {self.filename}"):
            sa1_code = row['SA1_CODE21']
            sa2_code = row['SA2_CODE21']

            # Skip the row if SA2_CODE21 is empty or None
            if pd.isna(sa2_code) or not sa2_code:
                continue

            # test
            filtered_df = sa2_gdf[sa2_gdf['SA2_CODE21'].astype(str) == str(sa2_code)]
            if filtered_df.empty:
                tqdm.write(f"Warning: SA2_CODE21 {sa2_code} from study area not found in {self.filename}.")
                continue
            sa2_row = filtered_df.iloc[0]

            # Get corresponding row in sa2_gdf using sa2_code
            sa2_row = sa2_gdf[sa2_gdf['SA2_CODE21'].astype(str) == str(sa2_code)].iloc[0]

            # Create a new dictionary to hold the new row
            new_row_dict = {'SA1_CODE21': sa1_code, 'SA2_CODE21': sa2_code, 'geometry': row['geometry']}

            # Add fields from sa2_row, possibly dividing them
            for field in sa2_gdf.columns:
                value = sa2_row[field]

                # Divide the value if the field is not in exclude_division_field_list
                if field not in exclude_division_field_list + ['INDIV_QLTY', 'OVR_QLTY']:
                    assert sa2_code in self.sa2_2_sa1_dict, f"sa2_code {sa2_code} not in sa2_2_sa1_dict"
                    value = self.divide_value(value, self.sa2_2_sa1_dict[sa2_code], sa2_code, field)

                new_row_dict[field] = value

            new_rows.append(new_row_dict)

        # Create a new GeoDataFrame
        new_gdf = gpd.GeoDataFrame(new_rows, geometry='geometry')
        return new_gdf

    @staticmethod
    def cleanse_geometry(gdf, study_area_gdf):
        """cleanse SA2 and SA1 geometry to SA1 from study area shp based on SA1_CODE21"""
        # Ensure the SA1_CODE21 columns are of the same type for proper comparison
        gdf['SA1_CODE21'] = gdf['SA1_CODE21'].astype(str)
        study_area_gdf['SA1_CODE21'] = study_area_gdf['SA1_CODE21'].astype(str)

        # Assert that all entries in gdf are also present in study_area_gdf
        assert set(gdf['SA1_CODE21']).issubset(
            set(study_area_gdf['SA1_CODE21'])), "Not all SA1_CODE21 values in gdf are present in study_area_gdf."

        # Merge the two GeoDataFrames based on SA1_CODE21, updating geometry and other attributes.
        merged_gdf = gdf.merge(study_area_gdf[['SA1_CODE21', 'geometry']], on='SA1_CODE21', how='left',
                               suffixes=('', '_new'))

        # At this point, given the assertion, 'geometry_new' should be non-null for all rows.
        # Update the geometry.
        merged_gdf['geometry'] = merged_gdf['geometry_new']

        # Drop the new geometry column
        merged_gdf.drop(columns=['geometry_new'], inplace=True)

        return merged_gdf
