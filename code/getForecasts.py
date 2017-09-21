"""
getForecasts: gets the forecasts from the weather services and saves them.
"""
import urllib
import json
import csv
import datetime
import os
import time
import optparse
import sys

def strNow():
    now = datetime.datetime.now()
    strnow = str(now).replace(" ", "_").replace(":", "-").split(".")[0].strip()
    return strnow

def getJSONfromURL(url, filename, service, city, state, forecast_type):
    loop = True
    sleep_time = 20 if service == "WUnderground" else 1
    counter = 0
    while loop:
        try:
            counter += 1
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            loop = False
        except ValueError:
            loop = True
            if counter <= 5:
                sys.stderr.write("%s could not find JSON objects for %s, %s for forecast type %s.  Trying again.\n" % (service, city, state, forecast_type))
                sys.stderr.flush()
            else:
                sys.stderr.write("%s could not find JSON objects for %s, %s for forecast type %s.  Exiting permanently.\n" % (service, city, state, forecast_type))
                sys.stderr.flush()
                return
            time.sleep(sleep_time)
            sleep_time *= 2
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
        
def getFileName(service, city, state, strnow, request_type):
    return service + "_" + city + state + "_" + strnow + "_" + request_type + ".json"

def getAccuWeather(city, state, API_Key, AccuKey, save_directory):
    service = "AccuWeather"
    strnow = strNow()
    url_5day = "https://dataservice.accuweather.com/forecasts/v1/daily/5day/%s?apikey=%s&details=true" % (str(AccuKey), str(API_Key))
    url_12hour = "https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/%s?apikey=%s&details=true" % (str(AccuKey), str(API_Key))
    file_5day = os.path.join(save_directory, getFileName("AccuWeather", city, state, strnow, "5day"))
    file_12hour = os.path.join(save_directory, getFileName("AccuWeather", city, state, strnow, "12hour"))
#     try:
    getJSONfromURL(url_5day, file_5day, service, city, state, "5day")
    getJSONfromURL(url_12hour, file_12hour, service, city, state, "12hour")
#     except ValueError:
#         sys.stderr.write("%s could not find JSON objects for %s, %s.\n" % ("AccuWeather", city, state))
#         sys.stderr.flush()
    

def getNWS(city, state, lat, lon, grid, save_directory):
    service = "NWS"
    strnow = strNow()
    url_grid = "https://api.weather.gov/gridpoints/%s" % (str(grid))
    url_forecast = "https://api.weather.gov/points/%s,%s/forecast" % (str(lat), str(lon))
    url_hourly = "https://api.weather.gov/points/%s,%s/forecast/hourly" % (str(lat), str(lon))
    file_grid = os.path.join(save_directory, getFileName("NWS", city, state, strnow, "grid"))
    file_forecast = os.path.join(save_directory, getFileName("NWS", city, state, strnow, "forecast"))
    file_hourly = os.path.join(save_directory, getFileName("NWS", city, state, strnow, "hourly"))
#     try:
    getJSONfromURL(url_grid, file_grid, service, city, state, "grid")
    getJSONfromURL(url_forecast, file_forecast, service, city, state, "forecast")
    getJSONfromURL(url_hourly, file_hourly, service, city, state, "hourly")
#     except ValueError:
#         sys.stderr.write("%s could not find JSON objects for %s, %s.\n" % ("NWS", city, state))
#         sys.stderr.flush()

def getDarkSky(city, state, API_Key, lat, lon, save_directory):
    service = "DarkSky"
    strnow = strNow()
    url = "https://api.darksky.net/forecast/%s/%s,%s" % (str(API_Key), str(lat), str(lon))
    file_latlon = os.path.join(save_directory, getFileName("DarkSky", city, state, strnow, "latlon"))
#     try:
    getJSONfromURL(url, file_latlon, service, city, state, "latlon")
#     except ValueError:
#         sys.stderr.write("%s could not find JSON objects for %s, %s.\n" % ("DarkSky", city, state))
#         sys.stderr.flush()

def getWUnderground(city, state, API_Key, save_directory):
    service = "WUnderground"
    strnow = strNow()
    url_forecast = "https://api.wunderground.com/api/%s/forecast/q/%s/%s.json" % (str(API_Key), str(state), str(city))
    url_hourly = "https://api.wunderground.com/api/%s/hourly/q/%s/%s.json" % (str(API_Key), str(state), str(city))
    file_forecast = os.path.join(save_directory, getFileName("WUnderground", city, state, strnow, "forecast"))
    file_hourly = os.path.join(save_directory, getFileName("WUnderground", city, state, strnow, "hourly"))
#     try:
    getJSONfromURL(url_forecast, file_forecast, service, city, state, "forecast")
    getJSONfromURL(url_hourly, file_hourly, service, city, state, "hourly")
#     except ValueError:
#         sys.stderr.write("%s could not find JSON objects for %s, %s.\n" % ("WUnderground", city, state))
#         sys.stderr.flush()

def getCities(cities_location):
    cityDict = {}
    with open(cities_location, 'r') as csvfile:
        cityReader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        first = True
        for row in cityReader:
            if first:
                first = False
                continue
            else:
                key = row[0] + ", " + row[1]
                latLong = (float(row[2]), float(row[3]), int(row[4]), str(row[5]))
                cityDict[key] = latLong
    return cityDict

def getAPIKeys(keys_location):
    APIDict = {}
    with open(keys_location, 'r') as csvfile:
        APIReader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        first = True
        for row in APIReader:
            if first:
                first = False
                continue
            else:
                APIDict[str(row[0])] = str(row[1])
    return APIDict

def getAll(cityDict, APIDict, save_directory, sleep_time = 30):
    first = True
    myKeys = cityDict.keys()
    myKeys.sort()
    for key in myKeys:
        if first:
            first = False
        else:
            time.sleep(sleep_time)
        
        cityState = key.split(",")
        city = cityState[0].strip()
        state = cityState[1].strip()
        lat = str(cityDict[key][0])
        lon = str(cityDict[key][1])
        AccuKey = str(cityDict[key][2])
        grid = str(cityDict[key][3])
        getNWS(city, state, lat, lon, grid, save_directory)
        getDarkSky(city, state, APIDict["DarkSky"], lat, lon, save_directory)
        getAccuWeather(city, state, APIDict["AccuWeather"], AccuKey, save_directory)
        getWUnderground(city, state, APIDict["WUnderground"], save_directory)
        sys.stderr.write("Finished with:\t%s\t%s\n" % (city, state))
        sys.stderr.flush()

def executeGet(options, args, p, now):
    try:
        my_time = int(options.sleep)
    except ValueError:
        my_time = 30
        sys.stderr.write("The sleep time could not be converted to an int.  Using the default value.")
    city_location = options.cities
    api_location = options.api
    save_directory = options.directory
    if not os.path.exists(api_location):
        p.error("The API key location could not be found: %s" % api_location)
    if not os.path.exists(city_location):
        p.error("The city location could not be found: %s" % city_location)
    if not os.path.isdir(save_directory):
        p.error("The save directory %s does not exist." % (save_directory))
    newpath = os.path.join(save_directory, str(now.date()) + "_" + str(now.hour))
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    sys.stderr.write("Created date hour directory at %s.\n" % (str(now)))
    sys.stderr.flush()
    cityDict = getCities(city_location)
    APIDict = getAPIKeys(api_location)
    getAll(cityDict, APIDict, newpath, sleep_time = my_time)

def getReport(now, later):
    return "Getting the forecasts took time:\t%s\n" % (str(later - now))

def main():
    now = datetime.datetime.now()
    usage = "usage: %prog [options] "
    description = "Get forecasts"
    p = optparse.OptionParser(usage = usage,
                              description = description,)
    p.add_option('--cities', '-c', help = 'The file location that stores the city location information. [default: %default]', default = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\LatLongCities.csv')
    p.add_option('--api', '-a', help = 'The location of the file that stores the API key information. [default: %default]', default = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\Weather_API_Keys.csv')
    p.add_option('--directory', '-d', help = 'The location of the directory to save forecast files to. [default: %default]', default = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\Data')
    p.add_option('--sleep', '-s', help = 'The number of seconds inbetween getting forecast information for a city to sleep. [default: %default]', default = 30)
    options, args = p.parse_args()
    executeGet(options, args, p, now)
    later = datetime.datetime.now()
    report = getReport(now, later)
    sys.stderr.write(report)

if __name__ == "__main__":
    main()