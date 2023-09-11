import os
import pandas as pd
import geopandas as gpd

# Read the CSV file into a DataFrame
csv_path = "../_data/study area/CG_SA1_2016_SA1_2021.csv"
csv_df = pd.read_csv(csv_path)

# Read the 2021 study area Shapefile into a GeoDataFrame
shapefile_2021_path = "../_data/study area/ausurbhi_study_area_2021.shp"
gdf_2021 = gpd.read_file(shapefile_2021_path)

# Loop through each .shp file in the specified folder
folder_path = "../data/AusUrbHI HVI data processed/ABS 2016"
for filename in os.listdir(folder_path):
    if filename.endswith(".shp"):
        file_path = os.path.join(folder_path, filename)

        # Read the Shapefile into a GeoDataFrame
        gdf = gpd.read_file(file_path)

        # Create an empty GeoDataFrame to store processed rows
        new_gdf = gpd.GeoDataFrame(columns=gdf.columns)

        # Iterate through each row in the Shapefile
        for idx, row in gdf.iterrows():
            sa1_2016 = str(row['SA1_MAIN16'])

            # Check if sa1_2016 exists in the csv file
            assert sa1_2016 in csv_df['SA1_MAINCODE_2016'].astype(str).values

            # Find corresponding 2021 codes and their ratios
            matches = csv_df[csv_df['SA1_MAINCODE_2016'].astype(str) == sa1_2016]

            if len(matches) > 1:
                for _, match in matches.iterrows():
                    new_row = row.copy()

                    # Replace SA1_MAIN16 and update geometry
                    sa1_2021 = match['SA1_CODE_2021']
                    new_row['SA1_MAIN16'] = sa1_2021
                    new_row['geometry'] = gdf_2021[gdf_2021['SA1_CODE21'] == sa1_2021].iloc[0]['geometry']

                    # Update other columns
                    for col in new_row.index:
                        if col not in ['Shape', 'id', 'SA1_MAIN16', 'sa1_7dig16']:
                            try:
                                val = float(new_row[col])
                                new_row[col] = val * match['RATIO_FROM_TO']
                            except ValueError:
                                pass

                    # Append the new row to the new GeoDataFrame
                    new_gdf = new_gdf.append(new_row)
            else:
                new_gdf = new_gdf.append(row)

        # Save the new GeoDataFrame to a new Shapefile
        output_filename = filename.replace('.shp', '_2021_concordance.shp')
        output_path = os.path.join("../_data/AusUrbHI HVI data processed/ABS 2016 by 2021 concordance", output_filename)
        new_gdf.to_file(output_path)
