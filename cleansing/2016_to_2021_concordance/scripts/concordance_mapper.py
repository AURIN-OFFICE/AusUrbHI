import os
import geopandas as gpd
import pandas as pd
from geopandas import GeoDataFrame
from tqdm import tqdm


class ConcordanceMapper:
    def __init__(self, mapping_csv_df, study_area_gdf, csv_16_column, csv_21_column, filename, file_path,
                 shp_16_field, shp_21_field, exclude_division_field_list, output_folder_path):
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

    def map(self):
        # Drop NA values and standardize the data type for the 2016 column in mapping_csv_df
        self.mapping_csv_df.dropna(subset=[self.csv_16_column], inplace=True)
        self.mapping_csv_df[self.csv_16_column] = self.mapping_csv_df[self.csv_16_column].astype(float).astype('int64').astype(str)

        # Read shapefile data into a GeoDataFrame
        gdf = gpd.read_file(self.file_path)

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
            temp = pd.DataFrame()
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
                            val = float(new_row[col])
                            new_row[col] = round(val * match['RATIO_FROM_TO'], 1)
                        except ValueError:
                            pass

                # Update quality indicators
                new_row['RATIO'] = match['RATIO_FROM_TO']
                new_row['INDIV_QLTY'] = match['INDIV_TO_REGION_QLTY_INDICATOR']
                new_row['OVR_QLTY'] = match['OVERALL_QUALITY_INDICATOR']

                temp = temp._append(new_row, ignore_index=True)

            # in case of n:1 mapping from 2016 to 2021, sum field values in temp other than those from
            # self.exclude_division_field_list or RATIO, INDIV_QLTY, and OVR_QLTY. Keep the first row's
            # values for the latter ones.
            if len(temp) > 1:
                original_columns = temp.columns.tolist()
                temp = {
                    field: (temp[field].iloc[0] if field in self.exclude_division_field_list else temp[field].sum())
                    for field in temp.columns}
                result_order = list(temp.keys())
                assert original_columns == result_order, "Column order has changed"
                temp["RATIO"] = "merged"
                temp["INDIV_QLTY"] = "merged"
                temp["OVR_QLTY"] = "merged"

            new_rows = new_rows._append(temp, ignore_index=True)

        # Create new GeoDataFrame with updated rows
        new_gdf = GeoDataFrame(new_rows, geometry='geometry', crs=self.study_area_gdf.crs)
        new_gdf.rename(columns={self.shp_16_field: self.shp_21_field}, inplace=True)
        assert len(new_gdf) == len(gdf)

        # Save the new GeoDataFrame as a shapefile
        output_filename = self.filename.replace('.shp', '_2021_concordance.shp')
        output_path = os.path.join(self.output_folder_path, output_filename)
        new_gdf.to_file(output_path)
