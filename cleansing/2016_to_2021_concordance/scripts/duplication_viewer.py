import pandas as pd
import geopandas as gpd

# Set display options to ensure no omission in the console
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)  # Adjust the width to prevent wrapping of lines, if necessary

file = "../../../_data/study area/CG_SA1_2016_SA1_2021.csv"
data = pd.read_csv(file)

# Filter only code with value in study area SA1_CODE21 field
study_area = "../../../_data/study area/ausurbhi_study_area_2021.shp"
study_area_data = gpd.read_file(study_area)
study_area_sa1_codes = study_area_data['SA1_CODE21']
data = data[data['SA1_CODE_2021'].isin(study_area_sa1_codes)]

# Identify the duplicated 'SA1_CODE_2021' values
duplicated_sa1_codes = data['SA1_CODE_2021'][data['SA1_CODE_2021'].duplicated(keep=False)]

# Filter the DataFrame to only include the duplicated 'SA1_CODE_2021' values
duplicated_data = data[data['SA1_CODE_2021'].isin(duplicated_sa1_codes)]

# Convert 'RATIO_FROM_TO' to percentage format and group by 'SA1_CODE_2021'
duplicated_with_ratios = (
    duplicated_data.assign(RATIO_FROM_TO=lambda x: x['RATIO_FROM_TO'].apply(lambda y: f"{y:.1%}"))
    .groupby('SA1_CODE_2021')['RATIO_FROM_TO']
    .apply(list)
    .reset_index()
)

# Print the resulting DataFrame without omission
print(duplicated_with_ratios.to_string(index=False))
