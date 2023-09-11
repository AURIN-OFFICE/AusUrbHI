import os
import geopandas as gpd
from tqdm import tqdm


class ConcordanceMapper:
    def __init__(self,
                 csv_df,
                 study_area_df,
                 csv_16_column,
                 csv_21_column,
                 filename,
                 file_path,
                 shp_16_field,
                 shp_21_field,
                 exclude_division_field_list,
                 output_folder_path):
        self.csv_df = csv_df
        self.study_area_df = study_area_df
        self.csv_16_column = csv_16_column
        self.csv_21_column = csv_21_column
        self.filename = filename
        self.file_path = file_path
        self.shp_16_field = shp_16_field
        self.shp_21_field = shp_21_field
        self.exclude_division_field_list = exclude_division_field_list
        self.output_folder_path = output_folder_path

    def map(self):
        # Read the CSV file into a DataFrame
        self.csv_df.dropna(subset=[self.csv_16_column], inplace=True)
        self.csv_df[self.csv_16_column] = self.csv_df[self.csv_16_column].astype(float).astype('int64').astype(str)

        # Read the Shapefile into a GeoDataFrame
        gdf = gpd.read_file(self.file_path)

        # Create an empty GeoDataFrame to store processed rows
        new_gdf = gpd.GeoDataFrame(columns=gdf.columns)

        # Iterate through each row in the Shapefile
        for idx, row in tqdm(gdf.iterrows(), total=len(gdf), desc=f"processing {self.filename}"):
            sa1_2016 = str(row[self.shp_16_field])

            # Check if sa1_2016 exists in the csv file
            assert sa1_2016 in self.csv_df[self.csv_16_column].values

            # Find corresponding 2021 codes and their ratios
            matches = self.csv_df[self.csv_df[self.csv_16_column] == sa1_2016]

            if len(matches) > 1:
                for _, match in matches.iterrows():
                    new_row = row.copy()

                    # Replace SA1_MAIN16 and update geometry
                    sa1_2021 = match[self.csv_21_column]
                    new_row[self.shp_16_field] = sa1_2021
                    if sa1_2021 in self.study_area_df[self.shp_21_field].values:
                        new_row['geometry'] = \
                            self.study_area_df[self.study_area_df[self.shp_21_field] == sa1_2021].iloc[0]['geometry']
                    else:
                        pass

                    # Update other columns
                    for col in new_row.index:
                        if col not in self.exclude_division_field_list:
                            try:
                                val = float(new_row[col])
                                new_row[col] = round(val * match['RATIO_FROM_TO'])
                            except ValueError:
                                pass

                    # Append the new row to the new GeoDataFrame
                    new_gdf = new_gdf._append(new_row)
            else:
                new_gdf = new_gdf._append(row)

        # Save the new GeoDataFrame to a new Shapefile
        new_gdf.rename(columns={self.shp_16_field: self.shp_21_field}, inplace=True)
        output_filename = self.filename.replace('.shp', '_2021_concordance.shp')
        output_path = os.path.join(self.output_folder_path,
                                   output_filename)
        new_gdf.to_file(output_path)
