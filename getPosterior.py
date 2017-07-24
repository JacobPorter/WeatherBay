"""
getPosterior: gets the posterior distribution arguments
from the prior and the likelihood distributions.
"""

import datetime
import csv
from pprint import pprint
import extractInfo
import getHistory
import getForecasts

def computePosteriorArguments(likelihoodDict, priorDict, n = 4):
    elements = extractInfo.dataElements
    posteriorDict = {}
    for element in elements:
        if element == 'precipAmount':
            alpha = priorDict[element][1] + n * likelihoodDict[element][1] #* 100 #Hundredths of an inch
            beta = priorDict[element][2] + n
            posteriorDict[element] = ("Gamma", alpha, beta)
        elif element == 'precipProbability':
            alpha = priorDict[element][1] + n * likelihoodDict[element][1]
            beta = priorDict[element][2] + n - n * likelihoodDict[element][1]
            posteriorDict[element] = ("Beta", alpha, beta, alpha / (alpha + beta))
        else:
            avg_l = likelihoodDict[element][1]
            var_l = likelihoodDict[element][2]
            avg_p = priorDict[element][1]
            var_p = priorDict[element][2]
            mean_post = (avg_p / var_p + n * avg_l / var_l) / (1 / var_p + n / var_l)
            var_post = 1 / (1 / var_p + n / var_l)
            posteriorDict[element] = ("Normal", mean_post, var_post)
    return posteriorDict

def writePosteriorArguments(posteriors, outlocation, date):
    with open(outlocation, 'wb') as csvoutfile:
        header = ["CityState", "Date", "precipAmount", 'Alpha', 'Beta', 'precipProbability', 'Alpha', 'Beta', 'Predictive', 'temperatureMax',  'Average', 'Variance', 'temperatureMin', 'Average', 'Variance']
        posteriorWriter = csv.writer(csvoutfile, delimiter='\t', quotechar='"')
        posteriorWriter.writerow(header)
        cityStates = posteriors.keys()
        cityStates.sort()
        for cityState in cityStates:
            row = [cityState, date]
            keys = posteriors[cityState].keys()
            keys.sort()
            for key in keys:
                row += posteriors[cityState][key]
            posteriorWriter.writerow(map(str, row))
            
def getPosteriors():
    cityDict = getForecasts.getCities('G:\School\VA Tech Courses\ZhangLab\DataIncubator\LatLongCities.csv')
    outfile = 'C:\Users\jsporter\Downloads\Temp\Posteriors_2017_07_21.csv'
    date = datetime.date(2017, 07, 21)
    likelihoods = extractInfo.main()
    priors = getHistory.parseArgs()
    cityStates = cityDict.keys()
    cityStates.sort()
    posteriors = {}
    for cityState in cityStates:
        posteriors[cityState] = computePosteriorArguments(likelihoods[cityState][date], priors[cityState])
    pprint(posteriors)
    writePosteriorArguments(posteriors, outfile, date)
    return posteriors
    
def main():
    getPosteriors()

if __name__ == "__main__":
    main()
