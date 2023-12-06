import geopandas as gpd

abs_2016_g01_gdf = gpd.read_file(
    "../../_data/AusUrbHI HVI data processed/ABS 2016/datasource-AU_Govt_ABS_Census-UoM_AURIN_DB_2_sa1_g01_selected_person_characteristics_by_sex_census_2016_study_area_refined.shp")
abs_2021_g01_gdf = gpd.read_file(
    "../../_data/AusUrbHI HVI data processed/ABS 2021/main_G01_SA1_2021_NSW_study_area_refined.shp")
abs_2016_field = ["SA1_MAIN16", "tot_p"]
abs_2021_field = ["SA1_CODE21", "Tot_P_P"]

# create two csv files with two columns: SA1 code and population
abs_2016_g01_gdf = abs_2016_g01_gdf[abs_2016_field]
abs_2016_g01_gdf.columns = ["SA1_CODE", "population"]
abs_2016_csv_path = "../_data/abs_2016_population.csv"
abs_2016_g01_gdf.to_csv(abs_2016_csv_path, index=False)

abs_2021_g01_gdf = abs_2021_g01_gdf[abs_2021_field]
abs_2021_g01_gdf.columns = ["SA1_CODE", "population"]
abs_2021_csv_path = "../_data/abs_2021_population.csv"
abs_2021_g01_gdf.to_csv(abs_2021_csv_path, index=False)
