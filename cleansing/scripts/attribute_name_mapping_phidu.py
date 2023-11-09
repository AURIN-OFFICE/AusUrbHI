import json
import geopandas as gpd
from phidu_short_field_name_dict import phidu_short_field_name_dict


dict_title = "PHIDU - Prevalence of Selected Health Risk Factors - Adults (PHA) 2017-2018"
shapefile_name = "datasource-TUA_PHIDU-UoM_AURIN_DB_1_phidu_estimates_risk_factors_adults_pha_2017_18_study_area_refined.shp"
# dict_exclude = ["geometry", "yr", "sa2_maincode_2016", "sa2_name_2016"]
# shp_exclude = ["id", "geometry", "yr", "SA2_MAIN16", "sa2_name_2"]
dict_exclude = ["fid", "geom", "pha_code", "pha_name"]
shp_exclude = ["id", "fid", "geometry", "pha_code", "pha_name", "SA2_MAIN16"]

# dict_exclude = []
# shp_exclude = []
shapefile_path = "../../_data/AusUrbHI HVI data processed/PHIDU and NATSEM datasets/" + shapefile_name
dict_path = "../../_data/study area/2022-06-23-datasets_attribute_dictionary.json"
dict_data = json.load(open(dict_path))

long = []
for i in dict_data:
    if i["title"] == dict_title:
        attributes = i["attributes"]
        for j in attributes:
            if j["attributeName"]not in dict_exclude:
                long.append([j["attributeName"], j["attributeComments"]])

print("--------------------")
for index, row in enumerate(long):
    print(row[1])
    pass

print("--------------------")
temp = []
for index, row in enumerate(long):
    print(row[0])
    pass

print("--------------------")
# print shapefile fields
short = []
for i in gpd.read_file(shapefile_path).columns:
    if i not in shp_exclude:
        print(i)
        short.append(i)

print("--------------------")
assert len(short) == len(long)
matched = []
mapping = []
for i in short:
    for j in long:
        if j[0] in phidu_short_field_name_dict and i[:5] in phidu_short_field_name_dict[j[0]]:
            mapping.append([i, j[1]])
            long.remove(j)
            matched.append(i)
            break
unmatched = [i for i in short if i not in matched]
print(len(mapping), len(unmatched), len(long))
mapping += zip(unmatched, [i[1] for i in long])

print("--------------------")
for k in [i[1] for i in mapping]:
    print(k)

print("--------------------")
for k in [i[0] for i in mapping]:
    print(k)

