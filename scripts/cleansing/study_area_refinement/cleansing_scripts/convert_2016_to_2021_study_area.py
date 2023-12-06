import pandas as pd
import geopandas as gpd


def old():
    """
    deprecated, since it's noticed that study area geocode.csv is incomplete, e.g., missing 12302143901
    """
    # Step 1: Read study area geocode.csv and get all codes from "SA1 Main Code"
    df_study_area = pd.read_csv('../../../../_data/study area/study area geocode.csv')
    sa1_main_codes = df_study_area['SA1 Main Code'].tolist()

    # Step 2: Read CG_SA1_2016_SA1_2021.csv and get the full list of 2021 regions mapped from study area geocode.csv
    df_mapping = pd.read_csv('../_data/CG_SA1_2016_SA1_2021.csv')
    mapped_2021_regions = df_mapping[df_mapping['SA1_MAINCODE_2016'].isin(sa1_main_codes)]['SA1_CODE_2021'].tolist()

    # Step 3: Read SA1_2021_AUST_GDA2020.shp, filter based on field "SA1_CODE21" from the mapped 2021 regions
    gdf = gpd.read_file('../../_data/ASGS/SA1_2021_AUST_GDA2020.shp')
    filtered_gdf = gdf[gdf['SA1_CODE21'].isin(mapped_2021_regions)]

    # Step 4: Generate a new shapefile called "ausurbhi_study_area_2021.shp"
    filtered_gdf.to_file("../_data/study area/ausurbhi_study_area_2021.shp")


def new():
    # Step 1: Read study area sa1_nsw.shp and get all codes from "SA1_MAIN16"
    data = gpd.read_file('../../_data/study area/sa1_nsw.shp')
    sa1_main_codes = data['SA1_MAIN16'].tolist()

    # Step 2: Read CG_SA1_2016_SA1_2021.csv and get the full list of 2021 regions mapped from study area geocode.csv
    df_mapping = pd.read_csv('../_data/CG_SA1_2016_SA1_2021.csv')
    df_mapping['SA1_MAINCODE_2016'] = df_mapping['SA1_MAINCODE_2016'].apply(
        lambda x: str(int(x)) if not pd.isnull(x) else x)
    df_mapping['SA1_CODE_2021'] = df_mapping['SA1_CODE_2021'].apply(
        lambda x: str(x) if not pd.isnull(x) else x)
    mapped_2021_regions = set(df_mapping[df_mapping['SA1_MAINCODE_2016'].isin(sa1_main_codes)]['SA1_CODE_2021'].tolist())

    # Step 3: Read SA1_2021_AUST_GDA2020.shp, filter based on field "SA1_CODE21" from the mapped 2021 regions
    gdf = gpd.read_file('../../_data/ASGS/SA1_2021_AUST_GDA2020.shp')
    filtered_gdf = gdf[gdf['SA1_CODE21'].isin(mapped_2021_regions)]

    # Step 4: Generate a new shapefile called "ausurbhi_study_area_2021.shp"
    filtered_gdf.to_file("../_data/study area/ausurbhi_study_area_2021.shp")


new()
