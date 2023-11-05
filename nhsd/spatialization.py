import geopandas as gpd
import pandas as pd


def create_nhsd_shp():
    """Converts the NHSD CSV file to a shapefile, and calculates the number of services for each service name.
    """
    short_name_dict = {
        "confidential_address": "conf_addr",
        "parent_org_id_old": "porg_idold",
        "parent_org_id_new": "porg_idnew",
        "parent_org_name": "porg_name",
        "orgid": "orgid",
        "ord_id": "ord_id",
        "org_name": "org_name",
        "addressline1": "addr_ln1",
        "suburb": "suburb",
        "state": "state",
        "postcode": "postcode",
        "gis_latitude": "gis_lat",
        "gis_longitude": "gis_long",
        "serviceid": "serv_id",
        "healthservice_id": "hs_id",
        "snomed_ct_au_concept_code": "snomed_code",
        "snomed_ct_au_concept_name": "snomed_nm",
        "languages_spoken": "lang_spkn",
        "people_employed": "peop_empl",
        "mon": "mon",
        "tues": "tues",
        "wed": "wed",
        "thurs": "thurs",
        "fri": "fri",
        "sat": "sat",
        "sun": "sun",
        "billing": "billing",
        "facilities": "facil"
    }

    input_file = "../_data/AusUrbHI HVI data unprocessed/NHSD/NHSD/20201207/wd/nhsd_nov2020_utf8.csv"
    temp_folder = "../_data/AusUrbHI HVI data unprocessed/NHSD"
    output_folder = "../_data/AusUrbHI HVI data processed/NHSD"

    data = pd.read_csv(input_file, encoding="utf-8")
    lat_column, lon_column = "gis_latitude", "gis_longitude"

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        data, geometry=gpd.points_from_xy(data[lon_column], data[lat_column])
    )

    # Set the CRS for WGS84 using EPSG code 4326
    gdf.set_crs(epsg=4326, inplace=True)

    # convert names to short names
    gdf.rename(columns=short_name_dict, inplace=True)

    # get service name statistics
    name_counts = gdf['snomed_nm'].value_counts()
    name_counts_json = name_counts.to_json()
    with open(f'{temp_folder}/service_name_count.json', 'w') as file:
        file.write(name_counts_json)

    gdf.to_file(f"{temp_folder}/nhsd_nov2020_utf8.shp")

create_nhsd_shp()