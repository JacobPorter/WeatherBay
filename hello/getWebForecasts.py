import os
import csv
import datetime
import sys
import time
import requests
import math
import json
from pprint import pprint
from collections import defaultdict

"""
Get weather forecast information from the weather services in JSON format.
"""
def strNow():
    now = datetime.datetime.now()
    strnow = str(now).replace(" ", "_").replace(":", "-").split(".")[0].strip()
    return strnow

def getJSONfromURL(url, service, city, state, forecast_type):
    loop = True
    sleep_time = 20 if service == "WUnderground" else 1
    counter = 0
    while loop:
        try:
            counter += 1
            #response = urllib.request(url)
            #data = json.loads(response.read())
            
            response = requests.get(url)
            if response.status_code == '200':
                data = response.json()
            else:
                print(response.status_code)
            #data = json.loads(response.read())
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
    return data
#     with open(filename, 'w') as outfile:
#         json.dump(data, outfile)
        
def getFileName(service, city, state, strnow, request_type):
    return service + "_" + city + state + "_" + strnow + "_" + request_type + ".json"

def getAccuWeather(city, state, API_Key, AccuKey, save_directory=None):
    service = "AccuWeather"
    #strnow = strNow()
    url_5day = "https://dataservice.accuweather.com/forecasts/v1/daily/5day/%s?apikey=%s&details=true" % (str(AccuKey), str(API_Key))
    #url_12hour = "https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/%s?apikey=%s&details=true" % (str(AccuKey), str(API_Key))
    #file_5day = os.path.join(save_directory, getFileName("AccuWeather", city, state, strnow, "5day"))
    #file_12hour = os.path.join(save_directory, getFileName("AccuWeather", city, state, strnow, "12hour"))
    return [json.load(open('./hello/static/AccuWeather_New_YorkNY.json'))]
    #return (getJSONfromURL(url_5day, service, city, state, "5day"))
    #getJSONfromURL(url_12hour, file_12hour, service, city, state, "12hour")
    

def getNWS(city, state, lat, lon, grid, save_directory=None):
    service = "NWS"
    #strnow = strNow()
    url_grid = "https://api.weather.gov/gridpoints/%s" % (str(grid))
    url_forecast = "https://api.weather.gov/points/%s,%s/forecast" % (str(lat), str(lon))
    #url_hourly = "https://api.weather.gov/points/%s,%s/forecast/hourly" % (str(lat), str(lon))
    #file_grid = os.path.join(save_directory, getFileName("NWS", city, state, strnow, "grid"))
    #file_forecast = os.path.join(save_directory, getFileName("NWS", city, state, strnow, "forecast"))
    #file_hourly = os.path.join(save_directory, getFileName("NWS", city, state, strnow, "hourly"))
    return [json.load(open('./hello/static/NWS_New_YorkNY_grid.json')), json.load(open('./hello/static/NWS_New_YorkNY_orecast.json'))]
    #return (getJSONfromURL(url_grid, service, city, state, "grid"), getJSONfromURL(url_forecast, service, city, state, "forecast"))
    #getJSONfromURL(url_hourly, file_hourly, service, city, state, "hourly")

def getDarkSky(city, state, API_Key, lat, lon, save_directory=None):
    service = "DarkSky"
    #strnow = strNow()
    url = "https://api.darksky.net/forecast/%s/%s,%s" % (str(API_Key), str(lat), str(lon))
    #file_latlon = os.path.join(save_directory, getFileName("DarkSky", city, state, strnow, "latlon"))
    return [json.load(open('./hello/static/DarkSky_New_YorkNY.json'))]
    #return (getJSONfromURL(url, service, city, state, "latlon"))

def getWUnderground(city, state, API_Key, save_directory=None):
    service = "WUnderground"
    #strnow = strNow()
    url_forecast = "https://api.wunderground.com/api/%s/forecast/q/%s/%s.json" % (str(API_Key), str(state), str(city))
    #url_hourly = "https://api.wunderground.com/api/%s/hourly/q/%s/%s.json" % (str(API_Key), str(state), str(city))
    #file_forecast = os.path.join(save_directory, getFileName("WUnderground", city, state, strnow, "forecast"))
    #file_hourly = os.path.join(save_directory, getFileName("WUnderground", city, state, strnow, "hourly"))
    return [json.load(open('./hello/static/WUnderground_New_YorkNY.json'))]
    #return (getJSONfromURL(url_forecast, service, city, state, "forecast"))
    
    #getJSONfromURL(url_hourly, file_hourly, service, city, state, "hourly")

"""
Extract the information from the JSON data
"""

dataElements = ['temperatureMax', 'temperatureMin', 'precipProbability', 'precipAmount', 'icon']

icon_search_order = ['snow', 'sleet', 'rain', 'fog', 'wind', 'cloudy', 'partly-cloudy-day', 'clear-day', 'none']

def translateDarkSky(DarkSky_icon):
    DarkSky_icon = str(DarkSky_icon)
    if DarkSky_icon == "partly-cloudy-night" or DarkSky_icon == "clear-night":
        return "clear-day"
    return DarkSky_icon

def extractDarkSky(json_iterable):
    forecast_data = json_iterable[0]
    def getDayData(dayDataD):
        #print(translateDarkSky(dayDataD['icon']))
        return dict(zip(dataElements, 
                        (dayDataD['temperatureMax'], 
                         dayDataD['temperatureMin'], 
                         dayDataD['precipProbability'], 
                         24 * float(dayDataD['precipIntensity']),
                         translateDarkSky(dayDataD['icon']) )))
    def getDate(forecastDict):
        unix_delta = datetime.timedelta(seconds = forecastDict['time'])
        return datetime.date(1970, 1, 1) + unix_delta
    result_dictionary = {}
    #pprint(forecast_data, open("forecast.data.txt", 'w'))
    prediction_list = forecast_data['daily']['data']
    for i in range(len(prediction_list)):
        result_dictionary[getDate(prediction_list[i])] = getDayData(prediction_list[i])
    return result_dictionary

def translateAccuWeather(accu_icon):
    if (accu_icon >= 1 and accu_icon <= 2) or (accu_icon >= 30 and accu_icon <= 31):
        return "clear-day"
    elif accu_icon >= 3 and accu_icon <= 4:
        return "partly-cloudy-day"
    elif accu_icon >= 6 and accu_icon <= 8:
        return "cloudy"
    elif accu_icon == 11 or accu_icon == 5:
        return "fog"
    elif (accu_icon >= 12 and accu_icon <= 18) or accu_icon == 26:
        return "rain"
    elif (accu_icon >= 19 and accu_icon <= 23) or accu_icon == 29:
        return "snow"
    elif accu_icon >= 24 and accu_icon <= 25:
        return "sleet"
    elif accu_icon == 32:
        return "wind"
    else:
        return 'none'

def extractAccuWeather(json_iterable):
    forecast_data = json_iterable[0]
    def getDayData(dayDataD):
        precipProbability = ((float(dayDataD['Day']['PrecipitationProbability']) + float(dayDataD['Night']['PrecipitationProbability'])) / 2.0)
        precipAmount = float(dayDataD['Day']['Rain']['Value']) + float(dayDataD['Night']['Rain']['Value'])
        temperatureMax = dayDataD['Temperature']['Maximum']['Value']
        temperatureMin = dayDataD['Temperature']['Minimum']['Value']
        icon = translateAccuWeather(dayDataD['Day']['Icon'])
        return dict(zip(dataElements, (temperatureMax, temperatureMin, precipProbability / 100.0, precipAmount, icon)))
    def getDate(forecastDict):
        my_date = forecastDict['Date'].split("T")[0].split('-')
        return datetime.date(int(my_date[0]), int(my_date[1]), int(my_date[2]))
    result_dictionary = {}
    try:
        prediction_list = forecast_data['DailyForecasts']
    except KeyError:
        pprint(forecast_data)
        return None
    for i in range(len(prediction_list)):
        result_dictionary[getDate(prediction_list[i])] = getDayData(prediction_list[i])
    return result_dictionary

def tranlateWUnderground(wunderground_icon):
    translater = {
        "snow" : ['chanceflurries', 'chancesnow', 'flurries', 'snow'],
        "cloudy" : ['unknown', 'cloudy', 'mostlycloudy'],
        "rain" : ['chancerain', 'chancetstorms', 'rain', 'tstorms'],
        "sleet" : ['chancesleet', 'sleet'],
        "clear-day" : ['clear', 'sunny', 'mostlysunny'],
        "partly-cloudy-day" : ['partlycloudy', 'partlysunny'],
        #"wind" : [],
        "fog" : ['fog', 'hazy']
    }
    for key in translater:
        for wu_icon in translater[key]:
            if wu_icon in wunderground_icon:
                return key
    return 'none'

def extractWUnderground(json_iterable):
    forecast_data = json_iterable[0]
    def getDayData(dayDataD):
        temperatureMax = float(dayDataD['high']['fahrenheit'])
        temperatureMin = float(dayDataD['low']['fahrenheit'])
        precipProbability = dayDataD['pop'] / 100.0
        precipAmount = dayDataD['qpf_allday']['in']
        icon = tranlateWUnderground(dayDataD['icon'])
        return dict(zip(dataElements, (temperatureMax, temperatureMin, precipProbability, precipAmount, icon)))
    def getDate(forecastDict):
        return datetime.date(forecastDict['date']['year'], forecastDict['date']['month'], forecastDict['date']['day'])
    result_dictionary = {}
    prediction_list = forecast_data['forecast']['simpleforecast']['forecastday']
    for i in range(len(prediction_list)):
        result_dictionary[getDate(prediction_list[i])] = getDayData(prediction_list[i])
    return result_dictionary

def getDate(validTime):
    date_list = list(map(int, validTime.split("T")[0].split("-")))
    return datetime.date(date_list[0], date_list[1], date_list[2])

def translateNWS(NWS_icon):
    if "Fair" in NWS_icon or 'Clear' in NWS_icon or 'Few Clouds' in NWS_icon or 'Hot' in NWS_icon or 'Cold' in NWS_icon or "Mostly Sunny" in NWS_icon or "Sunny" == NWS_icon:
        return 'clear-day'
    elif "Snow" in NWS_icon or 'Blizzard' in NWS_icon:
        return 'snow'
    elif "Pellets" in NWS_icon or "Ice" in NWS_icon or "Freezing" in NWS_icon or "Hail" in NWS_icon:
        return 'sleet'
    elif "Thunderstorm" in NWS_icon or "Showers" in NWS_icon or "Rain" in NWS_icon or "Drizzle" in NWS_icon or "Tropical" in NWS_icon or "Hurricane" in NWS_icon:
        return 'rain'
    elif "Fog" in NWS_icon or "Mist" in NWS_icon or 'Haze' in NWS_icon or 'Smoke' in NWS_icon or 'Dust' in NWS_icon or 'Sand' in NWS_icon:
        return 'fog'
    elif "Partly Cloudy" in NWS_icon or "Partly Sunny" in NWS_icon:
        return 'partly-cloudy-day'
    elif "Mostly Cloudy" in NWS_icon or 'Overcast' in NWS_icon or "Cloud" in NWS_icon:
        return 'cloudy'
    elif "Windy" in NWS_icon or "Tornado" in NWS_icon or "Breezy" in NWS_icon:
        return 'wind'
    else:
        return 'none'

def extractNWS(json_iterable):
    grid_data, forecast_data = json_iterable 
    results_dictionary = {}
    def finalizeValues(ValueDict):
        for element in ValueDict:
            if element == 'quantitativePrecipitation':
                ValueDict[element] = ValueDict[element][0]
            else:
                ValueDict[element] = ValueDict[element][0] / (ValueDict[element][1] + 0.0)
        if 'precipProbability' in ValueDict:
            ValueDict['precipProbability'] /= 100.0
    def putInResults(date, element, value):
        if date in results_dictionary:
            if element in results_dictionary[date]:
                stored = results_dictionary[date][element]
                results_dictionary[date][element] = (stored[0] + value, stored[1] + 1)
            else:
                results_dictionary[date][element] = (value, 1)
        else:
            results_dictionary[date] = {element: (value, 1)}
    def getDayData(dayDataD):
        maxTempList = dayDataD['properties']['maxTemperature']['values']
        minTempList = dayDataD['properties']['minTemperature']['values']
        probPrecList = dayDataD['properties']['probabilityOfPrecipitation']['values']
        quantPrecList = dayDataD['properties']['quantitativePrecipitation']['values']    
        for record in maxTempList:
            putInResults(getDate(record['validTime']), 
                         'temperatureMax', 
                         float(record['value']) * 1.8 + 32 )
        for record in minTempList:
            putInResults(getDate(record['validTime']), 
                         'temperatureMin', 
                         float(record['value']) * 1.8 + 32 )
        for record in probPrecList:
            putInResults(getDate(record['validTime']),
                         'precipProbability',
                         float(record['value']))
        for record in quantPrecList:
            putInResults(getDate(record['validTime']),
                         'precipAmount',
                         float(record['value']) * 0.0393701)
        for date in results_dictionary:
            finalizeValues(results_dictionary[date])
    def getIconData(forecast_data):
        period_list = forecast_data['properties']['periods']
        for period in period_list:
            if period['isDaytime']:
                results_dictionary[getDate(period['startTime'])]['icon'] = translateNWS(period['shortForecast'])
    getDayData(grid_data)
    getIconData(forecast_data)
    return results_dictionary

"""
Get the likelihood function
"""

def emptyIconDictionary():
    icon_list = ['clear-day', 'clear-night', 'partly-cloudy-day', 'partly-cloudy-night', 'cloudy', 'rain', 'sleet', 'snow', 'wind', 'fog', 'none']
    return {icon: 0 for icon in icon_list}

def computeWeightedAverageAndVariance(cityState, date, element, allForecasts, allWeights):
    if element == 'icon':
        icon_dictionary = emptyIconDictionary()
        for service in allForecasts:
            try:
                icon_dictionary[allForecasts[service][date][element]] += 1
            except KeyError:
                pass
            except TypeError:
                return None
        return icon_dictionary
    elementSelector = {'precipAmount': 3, 'precipProbability': 3, 'temperatureMax': 0, 'temperatureMin': 1}
    services = list(allForecasts.keys())
    services.sort()
    predictions = []
    for service in services:
        try:
            #print(service, cityState, date, element)
            #pprint(allForecasts)
            prediction = allForecasts[service][date][element]
        except KeyError:
            try:
                all_predicitons = [allForecasts[service][my_date][element] for my_date in allForecasts[service] if element in allForecasts[service][my_date]]
            except KeyError:
                print("KeyError with all_predictions")
                pprint(allForecasts)
            prediction = sum(all_predicitons) / (len(all_predicitons) + 0.0)
        except TypeError:
            return None
        predictions.append(prediction)
    total = allWeights[cityState]["Sums"][elementSelector[element]]
    weights = [allWeights[cityState][service][elementSelector[element]] / total for service in services]
    weighted_average = sum([i*j for i, j in zip(predictions, weights)])
    weighted_variance = sum([math.pow(prediction - weighted_average, 2) for prediction in predictions]) / (len(predictions) - 1.0)
    return {"Average": weighted_average, "Variance": weighted_variance}

def computeModelArguments(averageVariance, element):
    if averageVariance == None:
        return None
    if element == 'precipAmount': #Poisson
        return ("Poisson", averageVariance["Average"], averageVariance["Variance"]) #in hundredths of an inch.
    elif element == 'precipProbability': #Bernoulli
        return ("Bernoulli", averageVariance["Average"], averageVariance["Variance"])
    elif element == 'temperatureMax': #Normal
        return ("Normal", averageVariance["Average"], averageVariance["Variance"]) #Precision
    elif element == 'temperatureMin': #Normal
        return ("Normal", averageVariance["Average"], averageVariance["Variance"])
    elif element == 'icon':#Categorical
        maximum = -1
        maximizer = None
        for icon in icon_search_order:
            if averageVariance[icon] > maximum:
                maximum = averageVariance[icon]
                maximizer = icon
        return ("Categorical", averageVariance, maximizer)

def getAggregateForecastByCityDay(allForecasts, allWeights, cityState, sample_date):
    one_day = datetime.timedelta(days = 1)
    sample_date = sample_date - one_day
    likelihoodModels = {}
    for i in range(1, 5): #Number of days to forecast 
        forecast_date = sample_date + i * one_day
        likelihoodModels[forecast_date] = {}
        for element in dataElements:
            averageVariance = computeWeightedAverageAndVariance(cityState, forecast_date, element, allForecasts, allWeights)
            likelihoodModels[forecast_date][element] = computeModelArguments(averageVariance, element)
    return likelihoodModels

"""
Get the prior distribution from climatological history.
"""

def getDarkSkyHistory(API_Key, lat, lon, date, outdirectory = "hello/cache/history/"):
    unixtime = int(time.mktime(date.timetuple()))
    url = "https://api.darksky.net/forecast/%s/%s,%s,%s" % (str(API_Key), str(lat), str(lon), unixtime)
    try:
        filename = os.path.join(outdirectory, "DarkSky_history_%s_%s_%s.json" % (str(lat), str(lon), str(date)))
        if os.path.exists(filename):
            with open(filename, 'r') as infile:
                history = json.load(infile)
        else:
            response = requests.get(url)
            history = response.json()
            #response = urllib.request(url)
            #history = json.loads(response.read())
            with open(filename, 'w') as outfile:
                json.dump(history, outfile)
    except ValueError:
        sys.stderr.write("%s could not find JSON objects for %s, %s.\n" % ("DarkSky", lat, lon))
        sys.stderr.flush()
    record = history['daily']['data'][0]
    return dict(zip(dataElements, (record['temperatureMax'], 
                                               record['temperatureMin'], 
                                               record['precipProbability'], 
                                               record['precipIntensity'] * 24,
                                               translateDarkSky(record['icon'])
                                               )))

def getHistory(API_Key, lat, lon, date, num_days, outDirectory, thisDay = False):
    """
    Date should be the date for which the past will be computed for. (Not including the date)
    """
    results = {}
    if not thisDay:
        date = datetime.date(date.year - 1, date.month, date.day)
    averages = dict(zip(dataElements, [0] * len(dataElements)))
    del averages['icon']
    variance = dict(zip(dataElements, [0] * len(dataElements)))
    del variance['icon']
    icon_results = {}
    for i in range(num_days):
        past_date = datetime.date(date.year - i, date.month, date.day)
        try:
            results[past_date] = getDarkSkyHistory(API_Key, lat, lon, past_date, outDirectory)
            icon_results[past_date] = results[past_date]['icon']
            del results[past_date]['icon']
        except KeyError:
            sys.stderr.write("Could not find a field in %s, %s for day %s.  Skipping this date.\n" % (str(lat), str(lon), str(past_date)))
    counter = 0
    for key in results:
        counter += 1
        for element in results[key]:
            averages[element] += float(results[key][element])
    if counter != num_days:
        sys.stderr.write("Using %s records.\n" % (str(counter)))
    if not thisDay:
        for element in averages:
            averages[element] = averages[element] / counter
        for key in results:
            for element in results[key]:
                variance[element] += math.pow(float(results[key][element]) - averages[element], 2)
        for element in variance:
            try:
                variance[element] = variance[element] / (counter - 1)
            except ZeroDivisionError:
                variance[element] = 0 #float('inf')
    return {"Averages": averages, "Variance": variance, "Results": results, "Icon_Results": icon_results}

def estimateBeta(avg, var):
    try:
        i = (((avg*(1- avg)) / var) - 1 )
    except ZeroDivisionError:
        i = 0
    alpha = avg * i
    beta = (1 - avg) * i
    return [alpha, beta]

def estimateGamma(avg, var):
    """
    Returns shape (alpha) and rate (beta)
    """
    try:
        beta = avg / var
    except ZeroDivisionError:
        beta = 0
    alpha = avg * beta
    return [alpha, beta]

def estimateDirichlet(icon_results):
    """
    Returns concentration.
    """
    icon_counts = emptyIconDictionary()
    for my_date in icon_results:
        icon_counts[icon_results[my_date]] += 1
    maximum = -1
    maximizer = None
    for icon in icon_search_order:
        if icon_counts[icon] > maximum:
            maximum = icon_counts[icon]
            maximizer = icon
    return [icon_counts, maximizer]    
    
def getPriorArguments(history, doNotUseIcon = True):
    priorArguments = {}
    for element in dataElements:
        if element == 'icon':
            icon_results = history["Icon_Results"]
        else:
            avg = history["Averages"][element]
            var = history["Variance"][element]
        if element == 'precipProbability':
            priorArguments[element] = ["Beta"] + estimateBeta(avg, var)
        elif element == 'icon' and not doNotUseIcon:
            priorArguments[element] = ["Dirichlet"] + estimateDirichlet(icon_results)
        elif element == 'icon' and doNotUseIcon:
            priorArguments[element] = ["Dirichlet"] + [emptyIconDictionary(), '']
        elif element == 'precipAmount':
            priorArguments[element] = ["Gamma"] + estimateGamma(avg, var)
        else:
            priorArguments[element] = ["NormalGamma"] + [avg, var] +  estimateGamma(avg, var)
    return priorArguments


"""
Get the posterior hyperparameters.
"""

def computePosteriorArguments(likelihoodDict, priorDict, n = 4):
    elements = dataElements
    posteriorDict = {}
    for element in elements:
        if likelihoodDict[element] == None:
            return dict(zip(dataElements, [None] * len(dataElements)))
        elif element == 'precipAmount':
            alpha = priorDict[element][1] + n * likelihoodDict[element][1] #* 100 #Hundredths of an inch
            beta = priorDict[element][2] + n
            posteriorDict[element] = ("Gamma", alpha, beta)
        elif element == 'precipProbability':
            alpha = priorDict[element][1] + n * likelihoodDict[element][1]
            beta = priorDict[element][2] + n - n * likelihoodDict[element][1]
            posteriorDict[element] = ("Beta", alpha, beta, alpha / (alpha + beta))
        elif element == 'icon':
            concentration = {icon: priorDict[element][1][icon] +  likelihoodDict[element][1][icon] for icon in likelihoodDict[element][1]}
            maximizer = None
            maximum = -1
            for icon in icon_search_order:
                if concentration[icon] > maximum:
                    maximum = concentration[icon]
                    maximizer = icon
            posteriorDict[element] = ("Dirichlet", concentration, maximizer)
        else:
            avg_l = likelihoodDict[element][1]
            var_l = likelihoodDict[element][2]
            avg_p = priorDict[element][1]
            var_p = priorDict[element][2]
            try:
                mean_post = (avg_p / var_p + n * avg_l / var_l) / (1 / var_p + n / var_l)
            except ZeroDivisionError:
                print("ZeroDivisionError in computing the mean:", element, var_p, var_l)
            var_post = 1 / (1 / var_p + n / var_l)
            posteriorDict[element] = ("Normal", mean_post, var_post)
    return posteriorDict


"""
Get location information, keys, and forecast service weights.
"""

def get_API_keys():    
    return {'ACCU_KEY':os.environ['ACCU_KEY'], 'WU_KEY':os.environ['WU_KEY'], 'DARKSKY_KEY':os.environ['DARKSKY_KEY']}

def get_location(city_string, city_dictionary):
    cityState = cleanInput(city_string)
    location = city_dictionary[cityState]
    if not location:
        return None
    return location

def getCities(cities_location):
    cityDict = defaultdict(lambda: None)
    with open(cities_location, 'r') as csvfile:
        cityReader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        next(cityReader)
        for row in cityReader:
                key = row[0] + ", " + row[1]
                cityDict[key] = {'city': row[0], 'state': row[1], 'lat': float(row[2]), 'lon': float(row[3]), 'accu_key': int(row[4]), 'grid': str(row[5])}
    return cityDict

def getWeightsFromFile(weight_directory, file_name):
    weights = {}
    with open(os.path.join(weight_directory, file_name), 'r') as csvfile:
        weightReader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(weightReader)        
        for row in weightReader:
            if row[0].startswith("Dark"):
                weights["DarkSky"] = list(map(lambda x: float(x.replace("%", "")), row[1:len(row)]))
            elif "Underground" in row[0]:
                weights["WUnderground"] = list(map(lambda x: float(x.replace("%", "")), row[1:len(row)]))
            elif row[0].startswith("Accu"):
                weights["AccuWeather"] = list(map(lambda x: float(x.replace("%", "")), row[1:len(row)]))
            elif row[0].startswith("NWS"):
                weights["NWS"] = list(map(lambda x: float(x.replace("%", "")), row[1:len(row)]))
    sums = []
    for i in range(len(weights["DarkSky"])):
        sums.append(sum([weights[service][i] for service in weights]))
    weights["Sums"] = sums
    return weights
            
def getWeights(cityState, weight_directory):
    onlyfiles = [f for f in os.listdir(weight_directory) if os.path.isfile(os.path.join(weight_directory, f)) and f.endswith(".csv")]
    key = cityState.replace(",", "").replace(" ", "")
    file_name = [file_name for file_name in onlyfiles if key in file_name]
    if len(file_name) == 0:
        return {}
    else:
        weights = getWeightsFromFile(weight_directory, file_name[0])
        #print('weights', weights)
        return weights

def getAllWeights(cities, weight_directory):
    #cities = getForecasts.getCities(cities_location).keys()
    return {cityState : getWeights(cityState, weight_directory) for cityState in cities}

def cleanInput(city_string):
    key_material = [field.strip() for field in city_string.split(',')]
    if len(key_material) != 2:
        return None
    city = '_'.join(key_material[0].split()).title()
    state = key_material[1].upper()
    cityState = city + ', ' + state
    return cityState
    
"""
The main entry point to get the forecast posterior distributions. 
"""
def get_forecasts(city_string, city_dictionary, api_key_dictionary, weight_dictionary):
    location = get_location(city_string, city_dictionary)
    if location == None:
        return None
    allForecasts = defaultdict(lambda: None)
    allForecasts["AccuWeather"] = extractAccuWeather(getAccuWeather(location['city'], location['state'], api_key_dictionary['ACCU_KEY'], location['accu_key']))
    allForecasts["DarkSky"] = extractDarkSky(getDarkSky(location['city'], location['state'], api_key_dictionary['DARKSKY_KEY'], location['lat'], location['lon']))
    allForecasts["NWS"] = extractNWS(getNWS(location['city'], location['state'], location['lat'], location['lon'], location['grid']))
    allForecasts["WUnderground"] = extractWUnderground(getWUnderground(location['city'], location['state'], api_key_dictionary['WU_KEY']))
    #today = datetime.datetime.now()
    #sample_date = datetime.date(today.year, today.month, today.day)
    sample_date = datetime.date(2017, 9, 16)
    prediction_date = datetime.date(2017, 9, 17)
    likelihoodModels = getAggregateForecastByCityDay(allForecasts, weight_dictionary, location['city'] + ', ' + location['state'], sample_date)
    #print("likelihood function:")
    #pprint(likelihoodModels)
    history = getHistory(api_key_dictionary['DARKSKY_KEY'], location['lat'], location['lon'], sample_date, 5, "./hello/cache/history/", thisDay = False)
    priorDict = getPriorArguments(history)
    #print("prior dist:")
    #pprint(priorDict)
    return computePosteriorArguments(likelihoodModels[prediction_date], priorDict)
    

if __name__ == '__main__':
    print(getCities('/home/jsporter/workspace/WeatherBay/hello/static/LatLongCities.csv'))
    print(get_forecasts('boston, ma', getCities('/home/jsporter/workspace/WeatherBay/hello/static/LatLongCities.csv'), get_API_keys(), None))
    #print(get_API_keys())