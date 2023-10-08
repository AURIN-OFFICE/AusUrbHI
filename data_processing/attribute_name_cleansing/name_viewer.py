import shapefile

file = "au-govt-abs-census-sa1-g59-method-of-travel-to-work-by-sex-census-2016-sa1-2016_study_area_refined_2021_concordance.shp"
path = "../../_data/AusUrbHI HVI data processed/ABS 2016 by 2021 concordance/" + file

sf = shapefile.Reader(path)
field_names = [field[0] for field in sf.fields[1:]]  # Skip the deletion flag
print(field_names)
