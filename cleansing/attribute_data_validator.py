import shapefile

file = "datasource-AU_Govt_ABS_Census-UoM_AURIN_DB_2_sa1_g39_dwelling_struct_by_hsehold_and_family_census_2016_study_area_refined_2021_concordance.shp"
path = "../../_data/AusUrbHI HVI data processed/ABS 2016 by 2021 concordance/" + file

sf = shapefile.Reader(path)
field_names = [field[0] for field in sf.fields[1:]]  # Skip the deletion flag
print(field_names)
