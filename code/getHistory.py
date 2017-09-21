"""
getHistory: compute the prior distribution arguments from historical 
climatological data from DarkSky.
"""
import urllib
import json
import csv
import datetime
import os
import time
import optparse
import sys
import copy
from pprint import pprint
import getForecasts
import extractInfo
import pickle
import math

def getDarkSkyHistory(API_Key, lat, lon, date, outdirectory):
    unixtime = int(time.mktime(date.timetuple()))
    url = "https://api.darksky.net/forecast/%s/%s,%s,%s" % (str(API_Key), str(lat), str(lon), unixtime)
    try:
        filename = os.path.join(outdirectory, "DarkSky_history_%s_%s_%s.json" % (str(lat), str(lon), str(date)))
        if os.path.exists(filename):
            with open(filename, 'r') as infile:
                history = json.load(infile)
        else:
            response = urllib.urlopen(url)
            history = json.loads(response.read())        
            with open(filename, 'w') as outfile:
                json.dump(history, outfile)
    except ValueError:
        sys.stderr.write("%s could not find JSON objects for %s, %s.\n" % ("DarkSky", lat, lon))
        sys.stderr.flush()
    record = history['daily']['data'][0]
    return dict(zip(extractInfo.dataElements, (record['temperatureMax'], 
                                               record['temperatureMin'], 
                                               record['precipProbability'], 
                                               record['precipIntensity'] * 24,
                                               extractInfo.translateDarkSky(record['icon'])
                                               )))
    
def getHistory(API_Key, lat, lon, date, num_days, outDirectory, thisDay = False):
    """
    Date should be the date for which the past will be computed for. (Not including the date)
    """
    results = {}
    if not thisDay:
        date = datetime.date(date.year - 1, date.month, date.day)
    averages = dict(zip(extractInfo.dataElements, [0] * len(extractInfo.dataElements)))
    del averages['icon']
    variance = dict(zip(extractInfo.dataElements, [0] * len(extractInfo.dataElements)))
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
    icon_counts = extractInfo.emptyIconDictionary()
    for my_date in icon_results:
        icon_counts[icon_results[my_date]] += 1
    maximum = -1
    maximizer = None
    for icon in extractInfo.icon_search_order:
        if icon_counts[icon] > maximum:
            maximum = icon_counts[icon]
            maximizer = icon
    return [icon_counts, maximizer]
        
    
def getPriorArguments(history):
    priorArguments = {}
    for element in extractInfo.dataElements:
        if element == 'icon':
            icon_results = history["Icon_Results"]
        else:
            avg = history["Averages"][element]
            var = history["Variance"][element]
        if element == 'precipProbability':
            priorArguments[element] = ["Beta"] + estimateBeta(avg, var)
        elif element == 'icon':
            priorArguments[element] = ["Dirichlet"] + estimateDirichlet(icon_results)
        elif element == 'precipAmount':
            priorArguments[element] = ["Gamma"] + estimateGamma(avg, var)
        else:
            priorArguments[element] = ["NormalGamma"] + [avg, var] +  estimateGamma(avg, var)
    return priorArguments

def writePriorArguments(priorArguments, cityState, date, priorWriter):
    row = [cityState, str(date)]
    elements = copy.copy(extractInfo.dataElements)
    elements.sort()
    for element in elements:
        row = row + priorArguments[element]
    priorWriter.writerow(row)
    
def setupPriorWriter(outfile):
    priorWriter = csv.writer(open(outfile, 'wb'), delimiter='\t', quotechar='"')
    header = ["CityState", "Date", "icon", "Concentration", "argMax", "precipAmount",  'Alpha', 'Beta', 'precipProbability', 'Alpha', 'Beta',  'temperatureMax',  'Average', 'Variance', 'Alpha', 'Beta', 'temperatureMin', 'Average', 'Variance', 'Alpha', 'Beta']
    priorWriter.writerow(header)
    return priorWriter

def writeActualWeather(actualWeather, date, outfile):
    actualWriter = csv.writer(open(outfile, 'wb'), delimiter='\t', quotechar='"')
    header = ["CityState", "Date", "icon", "expectedRainValue", "precipAmount", "precipProbability", 'temperatureMax', 'temperatureMin']
    actualWriter.writerow(header)
    cityStates = actualWeather.keys()
    cityStates.sort()
    elements = copy.copy(extractInfo.dataElements)
    elements.sort()
    for cityState in cityStates:
        row = [cityState, str(date), actualWeather[cityState]['Icon_Results'][date], actualWeather[cityState]['Averages']["precipAmount"] * actualWeather[cityState]['Averages']["precipProbability"]]
        for element in elements:
            if element != 'icon':
                row = row + [actualWeather[cityState]['Averages'][element]]
        actualWriter.writerow(row)

def runGetHistory(api_key_location, cities_location, prior_location, history_directory, date, past_days = 20, booleanDarkSkyHistory = True, thisDay = False, actual_outfile = "./actual_weather.csv"):
    DarkSkyKey = getForecasts.getAPIKeys(api_key_location)["DarkSky"]
    cityDict = getForecasts.getCities(cities_location)
    if not os.path.isdir(history_directory):
        os.makedirs(history_directory)
    if not os.path.isdir(os.path.dirname(prior_location)):
        os.makedirs(os.path.dirname(prior_location))
    allHistoriesFile = os.path.join(history_directory, "allHistories.pickle")
    #booleanDarkSkyHistory = True
    #thisDay = False
    #past_days = 20
    cityStateKeys = cityDict.keys()
    cityStateKeys.sort()
    if not thisDay:
        priorWriter = setupPriorWriter(prior_location)
    allPriorArguments = {}
    counter = 0
    allHistories = {}
    if not booleanDarkSkyHistory:
        allHistories = pickle.load(open(allHistoriesFile, 'rb'))
        pprint(allHistories)
    for cityState in cityStateKeys:
#         if counter >= 2:
#             break
        counter += 1
        if booleanDarkSkyHistory:
            latlon = cityDict[cityState]
            history = getHistory(DarkSkyKey, latlon[0], latlon[1], date, past_days, history_directory, thisDay = thisDay)
            allHistories[cityState] = history  
        else:
            history = allHistories[cityState]
        if not thisDay:
            priorArguments = getPriorArguments(history)
            allPriorArguments[cityState] = priorArguments
            writePriorArguments(priorArguments, cityState, date, priorWriter)
    if booleanDarkSkyHistory:
        pickle.dump(allHistories, open(allHistoriesFile, 'wb'))
    if thisDay:
        writeActualWeather(allHistories, date, actual_outfile)
    pprint(allHistories)
    pprint(allPriorArguments)
    return allPriorArguments
    
def main():
    date_time_string = "2017-07-22_11"
    date_to_get = datetime.date(2017, 07, 23)
    cities_location = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\LatLongCities.csv'
    output_directory = os.path.join("C:\Users\jsporter\Downloads\Temp", date_time_string)
    api_key_location = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\Weather_API_Keys.csv'
    prior_location = os.path.join(output_directory, "Priors_" + date_time_string + ".csv")
    actual_outfile = os.path.join(output_directory, "Actual_Weather_" + str(date_to_get) + ".csv")
    history_directory = os.path.join(output_directory, "DarkSky_PriorData_" + date_time_string)    
    runGetHistory(api_key_location, cities_location, prior_location, history_directory, date_to_get, past_days = 1, thisDay = True, actual_outfile = actual_outfile)
    
if __name__ == "__main__":
    main()