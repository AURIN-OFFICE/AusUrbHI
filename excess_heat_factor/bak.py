import ee
import json
import geopandas as gpd


class ModisTemperature:
    """
    This class is used to get the daily minimum and maximum temperatures from the MODIS dataset.
    NOTE: run earthengine authenticate before running this script.

    :param s_date: the start date
    :param e_date: the end date
    :param shp: the path to the study area shapefile
    """
    def __init__(self, s_date, e_date, shp):
        # Initialize the Earth Engine API
        ee.Authenticate()
        ee.Initialize()

        # Set the start and end dates
        self.start_date = s_date
        self.end_date = e_date

        # Get the study area shapefile
        self.study_area = gpd.read_file(shp)

        # Get GEE boundary_data
        self.dataset = ee.ImageCollection('MODIS/006/MOD11A1')

    def get_daily_temperature(self):
        """
        This function is used to get the daily minimum and maximum temperatures.
        @return: an ee.ImageCollection object containing the daily minimum and maximum temperatures
        """
        def day_night_temps(image):
            """
            This function is used to get the day and night temperatures from a single image.
            @param image: an ee.Image object
            @return: an ee.Image object containing the day and night temperatures
            """
            daytime = image.select('LST_Day_1km').multiply(0.02).subtract(273.15)
            nighttime = image.select('LST_Night_1km').multiply(0.02).subtract(273.15)
            return ee.Image(daytime).addBands(nighttime).copyProperties(image, ['system:time_start'])

        daily_temps = self.dataset.filterDate(self.start_date, self.end_date).map(day_night_temps)
        return daily_temps

    def get_temperature_extremes(self):
        """
        This function is used to get the daily minimum and maximum temperatures.
        @return: an ee.Dictionary object containing the daily minimum and maximum temperatures
        """
        daily_temps = self.get_daily_temperature()

        def min_max_temps(img, prev):
            """
            This function is used to get the minimum and maximum temperatures from a collection of images.
            @param img: an ee.Image object
            @param prev: an ee.Dictionary object
            @return: an ee.Dictionary object containing the minimum and maximum temperatures
            """
            prev = ee.Dictionary(prev)
            min_day = ee.Image(prev.get('min_day')).min(img.select('LST_Day_1km'))
            max_day = ee.Image(prev.get('max_day')).max(img.select('LST_Day_1km'))
            min_night = ee.Image(prev.get('min_night')).min(img.select('LST_Night_1km'))
            max_night = ee.Image(prev.get('max_night')).max(img.select('LST_Night_1km'))
            return ee.Dictionary(
        {'min_day': min_day, 'max_day': max_day, 'min_night': min_night, 'max_night': max_night})

        extreme_temps = daily_temps.iterate(min_max_temps, ee.Dictionary({
            'min_day': ee.Image.constant(100),
            'max_day': ee.Image.constant(-100),
            'min_night': ee.Image.constant(100),
            'max_night': ee.Image.constant(-100)
        }))

        return ee.Dictionary(extreme_temps)


if __name__ == '__main__':
    # Set the date range (2011-2021) and the study area
    start_date = '2011-01-01'
    end_date = '2021-12-31'
    study_area = 'boundary_data/sa1_nsw.shp'

    # Create an instance of the ModisTemperature class
    modis_temperature = ModisTemperature(start_date, end_date, study_area)

    # Get the temperature extremes
    extreme_temps = modis_temperature.get_temperature_extremes()

    # Print the temperature extremes as JSON
    print(json.dumps(extreme_temps.getInfo(), indent=2))
    