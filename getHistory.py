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
                                               record['precipIntensity'] * 24)))
    
def getHistory(API_Key, lat, lon, date, num_days, outDirectory, thisDay = False):
    """
    Date should be the date for which the past will be computed for. (Not including the date)
    """
    results = {}
    if not thisDay:
        date = datetime.date(date.year - 1, date.month, date.day)
    averages = dict(zip(extractInfo.dataElements, [0] * len(extractInfo.dataElements)))
    variance = dict(zip(extractInfo.dataElements, [0] * len(extractInfo.dataElements)))
    for i in range(num_days):
        past_date = datetime.date(date.year - i, date.month, date.day)
        try:
            results[past_date] = getDarkSkyHistory(API_Key, lat, lon, past_date, outDirectory)
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
            variance[element] = variance[element] / (counter - 1)
    return {"Averages": averages, "Variance": variance, "Results": results}
    
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
    
def getPriorArguments(history):
    priorArguments = {}
    for element in extractInfo.dataElements:
        avg = history["Averages"][element]
        var = history["Variance"][element]
        if element == 'precipProbability':
            priorArguments[element] = ["Beta"] + estimateBeta(avg, var)
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
    header = ["CityState", "Date", "precipAmount",  'Alpha', 'Beta', 'precipProbability', 'Alpha', 'Beta',  'temperatureMax',  'Average', 'Variance', 'Alpha', 'Beta', 'temperatureMin', 'Average', 'Variance', 'Alpha', 'Beta']
    priorWriter.writerow(header)
    return priorWriter

def parseArgs():
    DarkSkyKey = getForecasts.getAPIKeys('G:\School\VA Tech Courses\ZhangLab\DataIncubator\Weather_API_Keys.csv')["DarkSky"]
    cityDict = getForecasts.getCities('G:\School\VA Tech Courses\ZhangLab\DataIncubator\LatLongCities.csv')
    outfile = 'C:\Users\jsporter\Downloads\Temp\Priors_2017_07_21.csv'
    priorDataLocation = 'C:\Users\jsporter\Downloads\Temp\DarkSky_PriorData_2017_07_21'
    allHistoriesFile = os.path.join(priorDataLocation, "allHistories.pickle")
    booleanDarkSkyHistory = False
    thisDay = False
    date = datetime.date(2017, 07, 21)
    past_days = 20
    cityStateKeys = cityDict.keys()
    cityStateKeys.sort()
    priorWriter = setupPriorWriter(outfile)
    allPriorArguments = {}
    counter = 0
    allHistories = {}
    if not booleanDarkSkyHistory:
        allHistories = pickle.load(open(allHistoriesFile, 'rb'))
    for cityState in cityStateKeys:
#         if counter >= 2:
#             break
        counter += 1
        if booleanDarkSkyHistory:
            latlon = cityDict[cityState]
            history = getHistory(DarkSkyKey, latlon[0], latlon[1], date, past_days, priorDataLocation, thisDay = thisDay)
            allHistories[cityState] = history  
        else:
            history = allHistories[cityState]
        if not thisDay:
            priorArguments = getPriorArguments(history)
            allPriorArguments[cityState] = priorArguments
            writePriorArguments(priorArguments, cityState, date, priorWriter)
    if booleanDarkSkyHistory:
        pickle.dump(allHistories, open(allHistoriesFile, 'wb'))
    pprint(allHistories)
    pprint(allPriorArguments)
    return allPriorArguments
    
def main():
    parseArgs()
    
if __name__ == "__main__":
    main()
