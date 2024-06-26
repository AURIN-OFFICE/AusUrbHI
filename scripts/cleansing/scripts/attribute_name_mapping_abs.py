import json
import geopandas as gpd

dict_title = "ABS - Data by Region - Persons Born Overseas (SA2) 2011-2016"
shapefile_name = "abs_data_by_region_persons_born_overseas_asgs_sa2_2021_study_area_refined.shp"
# dict_exclude = ["geometry", "yr", "sa2_maincode_2016", "sa2_name_2016"]
# shp_exclude = ["id", "geometry", "yr", "SA2_MAIN16", "sa2_name_2"]
dict_exclude = ["fid", "geom", "pha_code", "pha_name"]
shp_exclude = ["id", "fid", "geometry", "pha_code", "pha_name", "SA2_MAIN16"]

# dict_exclude = []
# shp_exclude = []
shapefile_path = "../_data/AusUrbHI HVI data processed/other ABS datasets/" + shapefile_name
dict_path = "../../../_data/study area/2022-06-23-datasets_attribute_dictionary.json"
dict_data = json.load(open(dict_path))

long = []
for i in dict_data:
    if i["title"] == dict_title:
        attributes = i["attributes"]
        for j in attributes:
            if j["attributeName"]not in dict_exclude:
                print(j["attributeName"])
                long.append([j["attributeName"], j["attributeAbstract"]])

print("--------------------")

# print shapefile fields
short = []
for i in gpd.read_file(shapefile_path).columns:
    if i not in shp_exclude:
        print(i)
        short.append(i)

print("--------------------")

mapping = []
for i in short:
    for j in long:
        if i[:5] in j[0][:5]:
            mapping.append([i, j[1]])
            long.remove(j)
            break
print(len(mapping), len(short), len(long))
for k in [i[1] for i in mapping]:
    print(k)

