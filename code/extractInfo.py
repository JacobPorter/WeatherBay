"""
extractInfo: from the saved weather forecasts, parse the JSON data and 
return the weighted averages and variance from the forecasted values.
This file computes the arguments for the likelihood distributions.
"""
import json
import csv
import os
import datetime
import math
import sys
import copy
from pprint import pprint
import getForecasts

dataElements = ['temperatureMax', 'temperatureMin', 'precipProbability', 'precipAmount', 'icon']

icon_search_order = ['snow', 'sleet', 'rain', 'fog', 'wind', 'cloudy', 'partly-cloudy-day', 'clear-day', 'none']

def translateDarkSky(DarkSky_icon):
    DarkSky_icon = str(DarkSky_icon)
    if DarkSky_icon == "partly-cloudy-night" or DarkSky_icon == "clear-night":
        return "clear-day"
    return DarkSky_icon

def extractDarkSky(directory, filename):
    def getDayData(dayDataD):
        return dict(zip(dataElements, 
                        (dayDataD['temperatureMax'], 
                         dayDataD['temperatureMin'], 
                         dayDataD['precipProbability'], 
                         24 * float(dayDataD['precipIntensity']),
                         translateDarkSky(dayDataD['icon']) )))
    def getDate(forecastDict):
        unix_delta = datetime.timedelta(seconds = forecastDict['time'])
        return datetime.date(1970, 1, 1) + unix_delta
    forecast_file = os.path.join(directory, filename)
    result_dictionary = {}
    with open(forecast_file, 'r') as infile:
        forecast_data = json.load(infile)
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

def extractAccuWeather(directory, filename):
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
    forecast_file = os.path.join(directory, filename)
    result_dictionary = {}
    with open(forecast_file, 'r') as infile:
        forecast_data = json.load(infile)
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

def extractWUnderground(directory, filename):
    def getDayData(dayDataD):
        temperatureMax = float(dayDataD['high']['fahrenheit'])
        temperatureMin = float(dayDataD['low']['fahrenheit'])
        precipProbability = dayDataD['pop'] / 100.0
        precipAmount = dayDataD['qpf_allday']['in']
        icon = tranlateWUnderground(dayDataD['icon'])
        return dict(zip(dataElements, (temperatureMax, temperatureMin, precipProbability, precipAmount, icon)))
    def getDate(forecastDict):
        return datetime.date(forecastDict['date']['year'], forecastDict['date']['month'], forecastDict['date']['day'])
    forecast_file = os.path.join(directory, filename)
    result_dictionary = {}
    with open(forecast_file, 'r') as infile:
        forecast_data = json.load(infile)
        #pprint(forecast_data)
        prediction_list = forecast_data['forecast']['simpleforecast']['forecastday']
        for i in range(len(prediction_list)):
            result_dictionary[getDate(prediction_list[i])] = getDayData(prediction_list[i])
    return result_dictionary

def getDate(validTime):
    date_list = map(int, validTime.split("T")[0].split("-"))
    return datetime.date(date_list[0], date_list[1], date_list[2])

def translateNWS(NWS_icon):
    #print NWS_icon
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
        #sys.stderr.write("Could not find icon %s for NWS.\n" % NWS_icon)
        return 'none'

def extractNWS(directory, filename):
    grid_filename, forecast_filename = filename 
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
    grid_file = os.path.join(directory, grid_filename)
    with open(grid_file, 'r') as infile:
        grid_data = json.load(infile)
        #pprint(forecast_data, open(os.path.join(directory, grid_filename + ".pprint"), 'w'))
        getDayData(grid_data)
    forecast_file = os.path.join(directory, forecast_filename)
    with open(forecast_file, 'r') as infile:
        forecast_data = json.load(infile)
        getIconData(forecast_data)
    return results_dictionary

def getFiles(data_directory):
    onlyfiles = [f for f in os.listdir(data_directory) if os.path.isfile(os.path.join(data_directory, f))]
    file_dictionary = {"AccuWeather" : [], "DarkSky": [], "NWS": [], "WUnderground": [], "NWS_f": []}
    for file_name in onlyfiles:
        if file_name.startswith("AccuWeather") and "5day" in file_name:
            file_dictionary["AccuWeather"].append(file_name)
        elif file_name.startswith("DarkSky") and "latlon" in file_name:
            file_dictionary["DarkSky"].append(file_name)
        elif file_name.startswith("NWS"):
            if "grid" in file_name:
                file_dictionary["NWS"].append(file_name)
            elif "forecast" in file_name:
                file_dictionary["NWS_f"].append(file_name)
        elif file_name.startswith("WUnderground") and "forecast" in file_name:
            file_dictionary["WUnderground"].append(file_name)
    for key in file_dictionary:
        file_dictionary[key].sort()
    #file_dictionary["NWS"].sort(key=lambda x: whichCity(cities, x))
    #file_dictionary[""]
    file_dictionary["NWS"] = zip(file_dictionary["NWS"], file_dictionary["NWS_f"])
    del file_dictionary["NWS_f"]
    return file_dictionary

def getCity(city, state, file_list):
    key = city + state
    return [file_name for file_name in file_list if key in file_name]

def whichCity(cities, file_name):
    if isinstance(file_name, tuple):
        file_name = file_name[0]
    for cityState in cities:
        city = cityState.split(",")[0].strip()
        state = cityState.split(",")[1].strip()
        if city + state in file_name:
            return cityState

def useService(service, data_directory, file_name):
    if service.startswith("AccuWeather"):
        return extractAccuWeather(data_directory, file_name)
    elif service.startswith("DarkSky"):
        return extractDarkSky(data_directory, file_name)
    elif service.startswith("NWS"):
        return extractNWS(data_directory, file_name)
    elif service.startswith("WUnderground"):
        return extractWUnderground(data_directory, file_name)

def getAllForecasts(data_directory, cities_location):
    file_dictionary = getFiles(data_directory)
    cityDict = getForecasts.getCities(cities_location)
    cities = cityDict.keys()
    services = file_dictionary.keys()
    cities.sort()
    services.sort()
    allResults = {"AccuWeather" : {}, "DarkSky": {}, "NWS": {}, "WUnderground": {}}
    for service in file_dictionary:
        for file_name in file_dictionary[service]:
            cityState = whichCity(cities, file_name)
            allResults[service][cityState] = useService(service, data_directory, file_name)
    return allResults

def getWeightsFromFile(weight_directory, file_name):
    weights = {}
    with open(os.path.join(weight_directory, file_name), 'r') as csvfile:
        weightReader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        first = True
        for row in weightReader:
            if first:
                first = False
                continue
            else:
                if row[0].startswith("Dark"):
                    weights["DarkSky"] = map(lambda x: float(x.replace("%", "")), row[1:len(row)])
                elif "Underground" in row[0]:
                    weights["WUnderground"] = map(lambda x: float(x.replace("%", "")), row[1:len(row)])
                elif row[0].startswith("Accu"):
                    weights["AccuWeather"] = map(lambda x: float(x.replace("%", "")), row[1:len(row)])
                elif row[0].startswith("NWS"):
                    weights["NWS"] = map(lambda x: float(x.replace("%", "")), row[1:len(row)])
    sums = []
    for i in range(len(weights["DarkSky"])):
        sums.append(sum([weights[service][i] for service in weights]))
    weights["Sums"] = sums
    return weights     
            
def getWeights(cityState, weight_directory):
    onlyfiles = [f for f in os.listdir(weight_directory) if os.path.isfile(os.path.join(weight_directory, f)) and f.endswith(".csv")]
    key = cityState.replace(",", "").replace(" ", "")
    file_name = [file_name for file_name in onlyfiles if key in file_name][0]
    return getWeightsFromFile(weight_directory, file_name)

def getAllWeights(cities_location, weight_directory):
    cities = getForecasts.getCities(cities_location).keys()
    return {cityState : getWeights(cityState, weight_directory) for cityState in cities}

def emptyIconDictionary():
    icon_list = ['clear-day', 'clear-night', 'partly-cloudy-day', 'partly-cloudy-night', 'cloudy', 'rain', 'sleet', 'snow', 'wind', 'fog', 'none']
    return {icon: 0 for icon in icon_list}

def computeWeightedAverageAndVariance(cityState, date, element, allForecasts, allWeights):
    if element == 'icon':
        icon_dictionary = emptyIconDictionary()
        for service in allForecasts:
            try:
                icon_dictionary[allForecasts[service][cityState][date][element]] += 1
            except KeyError:
                pass
            except TypeError:
                return None
        return icon_dictionary
    elementSelector = {'precipAmount': 3, 'precipProbability': 3, 'temperatureMax': 0, 'temperatureMin': 1}
    services = allForecasts.keys()
    services.sort()
    #one_day = datetime.timedelta(days = 1)
    predictions = []
    for service in services:
        try:
            prediction = allForecasts[service][cityState][date][element]
        except KeyError:
            try:
                all_predicitons = [allForecasts[service][cityState][my_date][element] for my_date in allForecasts[service][cityState] if element in allForecasts[service][cityState][my_date]]
            except KeyError:
                pprint(allForecasts)
            prediction = sum(all_predicitons) / (len(all_predicitons) + 0.0)
        except TypeError:
            return None
        predictions.append(prediction)
#     try:
#         predictions = [allForecasts[service][cityState][date][element] for service in services]
#     except KeyError:
#         sys.stderr.write("service:\t%s\tcityState:\t%s\tdate:\t%s\telement:\t%s\n" % (service, cityState, str(date), element))
#         raise
    total = allWeights[cityState]["Sums"][elementSelector[element]]
    weights = [allWeights[cityState][service][elementSelector[element]] / total for service in services]
    weighted_average = sum([i*j for i, j in zip(predictions, weights)])
    weighted_variance = sum([math.pow(prediction - weighted_average, 2) for prediction in predictions]) / (len(predictions) - 1.0)
#     if element == "temperatureMax":
#         print "tempMax predictions for %s:\t%s\tTotal Weight:\t%s\tWeights:\t%s" % (cityState, str(predictions), str(total), str(weights))
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

def getAggregateForecast(allForecasts, allWeights, cities_location, sample_date):
    cityDict = getForecasts.getCities(cities_location)
    return {cityState : getAggregateForecastByCityDay(allForecasts, allWeights, cityState, sample_date) for cityState in cityDict}
        
def writeAggregateForecast(allAggregates, outlocation):
    with open(outlocation, 'wb') as csvoutfile:
        header = ["CityState", "Date", "icon", "Distribution", "Mode", "precipAmount",  'Average', 'Variance', 'precipProbability', 'Average', 'Variance',  'temperatureMax',  'Average', 'Variance', 'temperatureMin', 'Average', 'Variance']
        aggregateWriter = csv.writer(csvoutfile, delimiter='\t', quotechar='"')
        aggregateWriter.writerow(header)
        cityStates = allAggregates.keys()
        cityStates.sort()
        for cityState in cityStates:
            dates = allAggregates[cityState].keys()
            dates.sort()
            for date in dates:
                row = [cityState, str(date)]
                keys = allAggregates[cityState][date].keys()
                keys.sort()
                for key in keys:
                    try:
                        row += allAggregates[cityState][date][key]
                    except TypeError:
                        row += [None, None, None]
                aggregateWriter.writerow(map(str, row))
                
def writeIndividualForecasts(all_forecasts, all_forecasts_location):
    individual_writer = csv.writer(open(all_forecasts_location, 'wb'), delimiter='\t', quotechar='"')
    header = ["Service", "CityState", "Date", "icon", "precipAmount", "precipProbability", 'temperatureMax', 'temperatureMin']
    individual_writer.writerow(header)
    elements = copy.copy(dataElements)
    elements.sort()
    services = all_forecasts.keys()
    services.sort()
    for service in services:
        cityStates = all_forecasts[service].keys()
        cityStates.sort()
        for cityState in cityStates:
            dates = all_forecasts[service][cityState].keys()
            dates.sort()
            for date in dates:
                row = [service, cityState, str(date)]
                for element in elements:
                    try:
                        row.append(all_forecasts[service][cityState][date][element])
                    except KeyError:
                        row.append(None)
                        #pprint(all_forecasts[service])
                        #raise
                individual_writer.writerow(row)
                
def runExtractInfo(weight_directory, data_directory, cities_location, likelihood_location, all_forecasts_location, first_date_to_predict):
    if not os.path.isdir(os.path.dirname(likelihood_location)):
        os.makedirs(os.path.dirname(likelihood_location))
    all_forecasts = getAllForecasts(data_directory, cities_location)
    #pprint(all_forecasts, open(all_forecasts_location + ".json", 'w'))
    writeIndividualForecasts(all_forecasts, all_forecasts_location + ".csv")
    allAggregates = getAggregateForecast(all_forecasts, getAllWeights(cities_location, weight_directory), cities_location, first_date_to_predict)
    pprint(allAggregates)
    writeAggregateForecast(allAggregates, likelihood_location)
    return allAggregates
    
def main():
    first_date_to_predict = datetime.date(2017, 07, 22)
    date_time_string = "2017-07-22_11"
    weight_directory = "G:\School\VA Tech Courses\ZhangLab\DataIncubator\ForecastAdvisor\LastMonth"
    data_directory = os.path.join("C:\Users\jsporter\Downloads\Data", date_time_string)
    cities_location = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\LatLongCities.csv'
    output_directory = os.path.join("C:\Users\jsporter\Downloads\Temp", date_time_string)
    likelihood_location = os.path.join(output_directory, "Likelihoods_" + date_time_string + ".csv")
    all_forecasts_location = os.path.join(output_directory, "All_Forecasts_" + date_time_string)
    runExtractInfo(weight_directory, data_directory, cities_location, likelihood_location, all_forecasts_location, first_date_to_predict)

if __name__ == '__main__':
    main()
    