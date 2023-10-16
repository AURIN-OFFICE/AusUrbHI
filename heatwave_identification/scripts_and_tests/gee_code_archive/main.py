import ee
from pprint import pprint

ee.Initialize()

i_date = '2018-01-05'
f_date = '2018-01-07'

collection = ee.ImageCollection('MODIS/061/MOD11A1')\
    .select('LST_Day_1km', 'QC_Day')\
    .filterDate(i_date, f_date)

u_lon = 150.3715249
u_lat = -33.8469759
u_poi = ee.Geometry.Point(u_lon, u_lat)
scale = 1000

# Calculate and print the mean value of the LST collection at the point.
lst_urban_point = collection.mean().sample(u_poi, scale).first().get('LST_Day_1km').getInfo()
print('Average daytime LST at urban point:', round(lst_urban_point*0.02 -273.15, 2), '°C')

# Get the boundary_data for the pixel intersecting the point in urban area.
lst_u_poi = collection.getRegion(u_poi, scale).getInfo()

# Preview the result.
pprint(lst_u_poi[:5])
