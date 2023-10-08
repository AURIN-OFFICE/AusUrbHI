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
            if field in exclude_division_field_list + ['INDIV_QLTY', 'OVR_QLTY', 'RATIO']:
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
            print(f"Warning A: SA2_CODE21 {sa2_code} from study area not found in {self.filename}.")
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
            if field not in exclude_division_field_list + ['INDIV_QLTY', 'OVR_QLTY', 'RATIO']:
                assert sa2_code in self.sa2_2_sa1_dict, f"sa2_code {sa2_code} not in sa2_2_sa1_dict"
                value = self.divide_value(value, self.sa2_2_sa1_dict[sa2_code], sa2_code, field)

            new_row_dict[field] = value

        new_rows.append(new_row_dict)

    # Create a new GeoDataFrame
    new_gdf = gpd.GeoDataFrame(new_rows, geometry='geometry')
    return new_gdf


def cleanse_geometry(self, gdf, study_area_gdf):
    """cleanse SA2 and SA1 geometry to SA1 from study area shp based on SA1_CODE21"""
    # Ensure the SA1_CODE21 columns are of the same type for proper comparison
    gdf['SA1_CODE21'] = gdf['SA1_CODE21'].astype(str)
    study_area_gdf['SA1_CODE21'] = study_area_gdf['SA1_CODE21'].astype(str)

    # Create a dictionary from study_area_gdf for fast lookup
    study_area_dict = study_area_gdf.set_index('SA1_CODE21')['geometry'].to_dict()

    # Update the geometry in gdf based on the values in study_area_gdf
    for index, row in gdf.iterrows():
        sa1_code = row['SA1_CODE21']
        new_geometry = study_area_dict.get(sa1_code)
        try:
            assert new_geometry, f"Warning B: {sa1_code} from {self.filename} not found in study area shp"
            gdf.at[index, 'geometry'] = new_geometry
        except AssertionError as e:
            print(e)
            gdf.at[index, 'geometry'] = None  # Set geometry to None if assertion fails

    gdf.crs = 'EPSG:4283'
    return gdf