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
from pprint import pprint
import getForecasts

dataElements = ['temperatureMax', 'temperatureMin', 'precipProbability', 'precipAmount']

def extractDarkSky(directory, filename):
    def getDayData(dayDataD):
        return dict(zip(dataElements, 
                        (dayDataD['temperatureMax'], 
                         dayDataD['temperatureMin'], 
                         dayDataD['precipProbability'], 
                         24 * float(dayDataD['precipIntensity']))))
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


def extractAccuWeather(directory, filename):
    def getDayData(dayDataD):
        precipProbability = ((float(dayDataD['Day']['PrecipitationProbability']) + float(dayDataD['Night']['PrecipitationProbability'])) / 2.0)
        precipAmount = float(dayDataD['Day']['Rain']['Value']) + float(dayDataD['Night']['Rain']['Value'])
        temperatureMax = dayDataD['Temperature']['Maximum']['Value']
        temperatureMin = dayDataD['Temperature']['Minimum']['Value']
        return dict(zip(dataElements, (temperatureMax, temperatureMin, precipProbability / 100.0, precipAmount)))
    def getDate(forecastDict):
        my_date = forecastDict['Date'].split("T")[0].split('-')
        return datetime.date(int(my_date[0]), int(my_date[1]), int(my_date[2]))
    forecast_file = os.path.join(directory, filename)
    result_dictionary = {}
    with open(forecast_file, 'r') as infile:
        forecast_data = json.load(infile)
        prediction_list = forecast_data['DailyForecasts']
        for i in range(len(prediction_list)):
            result_dictionary[getDate(prediction_list[i])] = getDayData(prediction_list[i])
    return result_dictionary

def extractWUnderground(directory, filename):
    def getDayData(dayDataD):
        temperatureMax = float(dayDataD['high']['fahrenheit'])
        temperatureMin = float(dayDataD['low']['fahrenheit'])
        precipProbability = dayDataD['pop'] / 100.0
        precipAmount = dayDataD['qpf_allday']['in']
        return dict(zip(dataElements, (temperatureMax, temperatureMin, precipProbability, precipAmount)))
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

def extractNWS(directory, filename):
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
    forecast_file = os.path.join(directory, filename)
    with open(forecast_file, 'r') as infile:
        forecast_data = json.load(infile)
        #pprint(forecast_data, open(os.path.join(directory, filename + ".pprint"), 'w'))
        getDayData(forecast_data)
    return results_dictionary

def getFiles(data_directory):
    onlyfiles = [f for f in os.listdir(data_directory) if os.path.isfile(os.path.join(data_directory, f))]
    file_dictionary = {"AccuWeather" : [], "DarkSky": [], "NWS": [], "WUnderground": []}
    for file_name in onlyfiles:
        if file_name.startswith("AccuWeather") and "5day" in file_name:
            file_dictionary["AccuWeather"].append(file_name)
        elif file_name.startswith("DarkSky") and "latlon" in file_name:
            file_dictionary["DarkSky"].append(file_name)
        elif file_name.startswith("NWS") and "grid" in file_name:
            file_dictionary["NWS"].append(file_name)
        elif file_name.startswith("WUnderground") and "forecast" in file_name:
            file_dictionary["WUnderground"].append(file_name)
    for key in file_dictionary:
        file_dictionary[key].sort()
    return file_dictionary

def getCity(city, state, file_list):
    key = city + state
    return [file_name for file_name in file_list if key in file_name]

def whichCity(cities, file_name):
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

def computeWeightedAverageAndVariance(cityState, date, element, allForecasts, allWeights):
    elementSelector = {'precipAmount': 3, 'precipProbability': 3, 'temperatureMax': 0, 'temperatureMin': 1}
    services = allForecasts.keys()
    services.sort()
    #one_day = datetime.timedelta(days = 1)
    predictions = []
    for service in services:
        try:
            prediction = allForecasts[service][cityState][date][element]
        except KeyError:
            all_predicitons = [allForecasts[service][cityState][my_date][element] for my_date in allForecasts[service][cityState] if element in allForecasts[service][cityState][my_date]]
            prediction = sum(all_predicitons) / (len(all_predicitons) + 0.0)
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
    if element == 'precipAmount': #Poisson
        return ("Poisson", averageVariance["Average"], averageVariance["Variance"]) #in hundredths of an inch.
    elif element == 'precipProbability': #Bernoulli
        return ("Bernoulli", averageVariance["Average"], averageVariance["Variance"])
    elif element == 'temperatureMax': #Normal
        return ("Normal", averageVariance["Average"], averageVariance["Variance"]) #Precision
    elif element == 'temperatureMin': #Normal
        return ("Normal", averageVariance["Average"], averageVariance["Variance"])

def getAggregateForecastByCityDay(allForecasts, allWeights, cityState, sample_date):
    one_day = datetime.timedelta(days = 1)
    likelihoodModels = {}
    for i in range(1, 4): #Number of days to forecast 
        forecast_date = sample_date + i * one_day
        likelihoodModels[forecast_date] = {}
        for element in dataElements:
            averageVariance = computeWeightedAverageAndVariance(cityState, forecast_date, element, allForecasts, allWeights)
            modelArguments = computeModelArguments(averageVariance, element)
            likelihoodModels[forecast_date][element] = modelArguments
    return likelihoodModels

def getAggregateForecast(allForecasts, allWeights, cities_location, sample_date):
    cityDict = getForecasts.getCities(cities_location)
    return {cityState : getAggregateForecastByCityDay(allForecasts, allWeights, cityState, sample_date) for cityState in cityDict}
        
def writeAggregateForecast(allAggregates, outlocation):
    with open(outlocation, 'wb') as csvoutfile:
        header = ["CityState", "Date", "precipAmount",  'Average', 'Variance', 'precipProbability', 'Average', 'Variance',  'temperatureMax',  'Average', 'Variance', 'temperatureMin', 'Average', 'Variance']
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
                    row += allAggregates[cityState][date][key]
                aggregateWriter.writerow(map(str, row))
    
def main():
    #data_directory = "C:\Users\jsporter\Downloads\Temp"
    weight_directory = "G:\School\VA Tech Courses\ZhangLab\DataIncubator\ForecastAdvisor\LastMonth"
    #filename = "darksky_07192017"
    #wu_filename = "WU_Forecast5_Blacksburg_07202017.json"
    #accu_filename = "accuweather_blacksburg_forecast_07192017"
    #nws_filename = "NWS_BlacksburgVA_2017-07-20_23-29-27_grid.json"
    data_directory = "C:\Users\jsporter\Downloads\Data"
    cities_location = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\LatLongCities.csv'
    outlocation = "C:\Users\jsporter\Downloads\Temp\Likelihoods_2017_07_20.csv"
    #pprint(getAllForecasts(data_directory, cities_location), open("test.txt", 'w'))
    #pprint(getAllWeights(cities_location, weight_directory))
    allAggregates = getAggregateForecast(getAllForecasts(data_directory, cities_location), getAllWeights(cities_location, weight_directory), cities_location, datetime.date(2017, 07, 20))
    pprint(allAggregates)
    writeAggregateForecast(allAggregates, outlocation)
    return allAggregates
    #print getWeights("Blacksburg, VA", weight_directory)
    #nws_filename2 = "NWS_BlacksburgVA_2017-07-20_23-29-27_forecast.json"
    #extractDarkSky(data_directory, filename)
    #extractAccuWeather(data_directory, accu_filename)
    #extractWUnderground(data_directory, wu_filename)
    #Unix time: dt - datetime(1970,1,1)).total_seconds()
    #extractNWS(data_directory, nws_filename)

if __name__ == '__main__':
    main()
    
