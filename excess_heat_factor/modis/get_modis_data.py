# -*- coding: utf-8 -*-
import ee
import geopandas as gpd

study_area = gpd.read_file("boundary_data/boundaries.shp")
date = "2020-01-01"
