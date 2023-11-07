import json
import geopandas as gpd
from study_area_refinement.cleansing_scripts.phidu_short_field_name_dict import phidu_short_field_name_dict


dict_title = "NATSEM - Social and Economic Indicators - Synthetic Estimates SA2 2016"
shapefile_name = "datasource-UC_NATSEM-UoM_AURIN_DB_natsem_financial_indicators_synthetic_sa2_2016_study_area_refined.shp"
# dict_exclude = ["geometry", "yr", "sa2_maincode_2016", "sa2_name_2016"]
# shp_exclude = ["id", "geometry", "yr", "SA2_MAIN16", "sa2_name_2"]
dict_exclude = ["fid", "geom", "pha_code", "pha_name"]
shp_exclude = ["id", "fid", "geometry", "pha_code", "pha_name", "SA2_MAIN16"]

# dict_exclude = []
# shp_exclude = []
shapefile_path = "../_data/AusUrbHI HVI data processed/PHIDU and NATSEM datasets/" + shapefile_name
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

print("--------------------")

temp = []
for index, row in enumerate(long):
    print(row[0])

# # print shapefile fields
# short = []
# for i in gpd.read_file(shapefile_path).columns:
#     if i not in shp_exclude:
#         print(i)
#         short.append(i)
#
# print("--------------------")

# mapping = []
# for i in short:
#     for j in long:
#         if i[:5] in j[0][:5]:
#             mapping.append([i, j[1]])
#             long.remove(j)
#             break
# print(len(mapping), len(short), len(long))
# for k in [i[1] for i in mapping]:
#     print(k)

