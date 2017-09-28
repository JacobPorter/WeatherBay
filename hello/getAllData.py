import os
from getWebForecasts import extractDarkSky, extractAccuWeather, extractWUnderground, extractNWS, getDarkSkyHistory, getCities, get_API_keys

def getAllDataFromDirectory(prediction_directory, actual_directory, write_directory, cities_file, utc_offset = False):
    """
    Create a spreadsheet for each city.
    An observation (row) will have max, min etc. for all of the weather services at different times of prediction. It will indicate the date predicted.
    The response variables will be the actual temperatures, etc.
    2 obs X 4 services X 4 forecasts X 4 variables = 128 feature columns in a row + 4 response variables
    """
    city_dictionary = getCities(cities_file)
    actualGetter = getActualWeather(actual_directory, city_dictionary, get_API_keys())
    #For each day and for each city, get all the data and put it into a spreadsheet.


class getActualWeather:
    
    def __init__(self, actual_directory, city_dictionary, api_keys):
        self.actual_directory = actual_directory
        self.actual_dictionary = {}
        self.key = api_keys['DARKSKY_KEY']
        self.city_dictionary = city_dictionary
        
    def getActualWeather(self, cityState, date):
        return getDarkSkyHistory(self.key, self.city_dictionary[cityState]['lat'], self.city_dictionary[cityState]['lon'], date, outdirectory = self.actual_directory)
        

if __name__ == "__main__":
    prediction_directory = ""
    actual_directory = ""
    utc_offset = False
    write_directory = ""
    cities_file = '/home/jsporter/workspace/WeatherBay/hello/static/LatLongCities.csv'
    getAllDataFromDirectory(prediction_directory, actual_directory, write_directory, utc_offset = utc_offset)