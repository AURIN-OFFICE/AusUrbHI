import os
import json
import geopandas as gpd
import pandas as pd
import numpy as np
from geopandas import GeoDataFrame
from tqdm import tqdm

pd.set_option('display.max_columns', None)


class ConcordanceMapper:
    def __init__(self, mapping_csv_df, study_area_gdf, csv_16_column, csv_21_column, filename, file_path,
                 shp_16_field, shp_21_field, exclude_division_field_list, output_folder_path, geolevel):
        self.mapping_csv_df = mapping_csv_df
        self.study_area_gdf = study_area_gdf
        self.csv_16_column = csv_16_column
        self.csv_21_column = csv_21_column
        self.filename = filename
        self.file_path = file_path
        self.shp_16_field = shp_16_field
        self.shp_21_field = shp_21_field
        self.exclude_division_field_list = exclude_division_field_list
        self.output_folder_path = output_folder_path
        self.geolevel = geolevel
        self.population_dict = self._get_population_dict()
        self._get_attribute_full_name_dict = self._get_attribute_full_name_dict()

    def _get_population_dict(self):
        population_file = "sa1_population_dict.json" if self.geolevel == "sa1" else "sa2_population_dict.json"
        with open("scripts/" + population_file, 'r') as f:
            return json.load(f)

    @staticmethod
    def _get_attribute_full_name_dict():
        file = "scripts/Full Data Inventory.xlsx"
        df = pd.read_excel(file, sheet_name="Sheet1")
        # create dictionary of {dataItemNameAURIN: dataItemNameFull}
        return df.set_index('dataItemNameAURIN')['dataItemNameFull'].to_dict()

    def map(self):
        # Drop NA values and standardize the data type for the 2016 column in mapping_csv_df
        self.mapping_csv_df.dropna(subset=[self.csv_16_column], inplace=True)
        self.mapping_csv_df[self.csv_16_column] = (self.mapping_csv_df[self.csv_16_column].
                                                   astype(float).astype('int64').astype(str))

        # Read shapefile data into a GeoDataFrame
        gdf = gpd.read_file(self.file_path)
        gdf = gdf.replace([np.nan, None, '', '~', '-', '**', '*', 'nan'], 0)

        # Create dictionary for fast lookup of 2021 geometry
        study_area_dict = self.study_area_gdf.set_index(self.shp_21_field)['geometry'].to_dict()

        # Index mapping_csv_df for fast row retrieval
        lookup_mapping_csv_df = self.mapping_csv_df.set_index(self.csv_16_column)

        new_rows = pd.DataFrame()

        # Iterate over each row in the shapefile's GeoDataFrame
        for idx, row in tqdm(gdf.iterrows(), total=len(gdf), desc=f"processing {self.filename}"):
            sa1_2016 = str(row[self.shp_16_field])
            # Assert that the 2016 code exists in the csv
            assert sa1_2016 in lookup_mapping_csv_df.index

            # Find corresponding rows in mapping_csv_df for the 2016 code
            matches = lookup_mapping_csv_df.loc[[sa1_2016]]

            # Iterate over each corresponding row in mapping_csv_df to create a new row in GeoDataFrame
            for _, match in matches.iterrows():
                new_row = row.copy()
                sa1_2021 = match[self.csv_21_column]
                # Update with 2021 code
                new_row[self.shp_16_field] = sa1_2021

                # Update geometry for 2021, or keep the same if not available
                new_row['geometry'] = study_area_dict.get(sa1_2021, row['geometry'])

                # Update other fields based on ratio, except those in the exclude list
                for col in new_row.index:
                    if col not in self.exclude_division_field_list:
                        try:
                            val = float(new_row[col]) if new_row[col] else 0
                            if (col in self._get_attribute_full_name_dict and
                                    any(i in self._get_attribute_full_name_dict[col].lower()
                                        for i in ["average", "median", "mean"])):
                                new_row[col] = round(val, 2)
                            else:
                                new_row[col] = round(val * match['RATIO_FROM_TO'], 2)
                        except ValueError:
                            pass

                # Update quality indicators
                new_row['RATIO'] = match['RATIO_FROM_TO']
                new_row['INDIV_QLTY'] = match['INDIV_TO_REGION_QLTY_INDICATOR']
                new_row['OVR_QLTY'] = match['OVERALL_QUALITY_INDICATOR']

                new_rows = new_rows._append(new_row, ignore_index=True)
        new_rows.rename(columns={self.shp_16_field: self.shp_21_field}, inplace=True)

        # in case of n:1 mapping from 2016 to 2021, sum field values in temp other than those from
        # self.exclude_division_field_list or RATIO, INDIV_QLTY, and OVR_QLTY. Keep the first row's
        # values for the latter ones.
        merged_rows = pd.DataFrame(columns=new_rows.columns)
        grouped = new_rows.groupby(self.shp_21_field)

        for name, group in grouped:
            merged_row = {}
            for col in group.columns:
                # Exclude division fields are kept as they are
                if col in self.exclude_division_field_list:
                    merged_row[col] = group[col].iloc[0]
                # For specified fields, set the value to "merged"
                elif col in ["RATIO", "INDIV_QLTY", "OVR_QLTY"]:
                    if len(group) > 1:
                        merged_row[col] = "merged"
                    else:
                        merged_row[col] = group[col].iloc[0]
                # Calculate average or sum based on the column name criteria
                else:
                    if (col in self._get_attribute_full_name_dict and
                            any(i in self._get_attribute_full_name_dict[col].lower()
                                for i in ["average", "median", "mean"])):
                        merged_row[col] = group[col].mean()
                    else:
                        merged_row[col] = group[col].sum()
            # Add the merged row to the DataFrame
            merged_rows = merged_rows._append(merged_row, ignore_index=True)
        new_rows = merged_rows

        # Create new GeoDataFrame with updated rows
        new_gdf = GeoDataFrame(new_rows, geometry='geometry', crs=self.study_area_gdf.crs)

        # Save the new GeoDataFrame as a shapefile
        output_filename = self.filename.replace('.shp', '_2021_concordance.shp')
        output_path = os.path.join(self.output_folder_path, output_filename)
        new_gdf.to_file(output_path)
