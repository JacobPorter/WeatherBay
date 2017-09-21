import os
import datetime
import csv
from pprint import pprint
import extractInfo
import getHistory
import getForecasts

"""
getPosterior: gets the posterior distribution arguments
from the prior and the likelihood distributions.
"""

def computePosteriorArguments(likelihoodDict, priorDict, n = 4):
    elements = extractInfo.dataElements
    posteriorDict = {}
    for element in elements:
        if likelihoodDict[element] == None:
            return dict(zip(extractInfo.dataElements, [None] * len(extractInfo.dataElements)))
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
            for icon in extractInfo.icon_search_order:
                if concentration[icon] > maximum:
                    maximum = concentration[icon]
                    maximizer = icon
            posteriorDict[element] = ("Dirichlet", concentration, maximizer)
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
        header = ["CityState", "Date", "icon", "concentration", "argMax", "precipAmount", 'Alpha', 'Beta', 'precipProbability', 'Alpha', 'Beta', 'Predictive', 'temperatureMax',  'Average', 'Variance', 'temperatureMin', 'Average', 'Variance']
        posteriorWriter = csv.writer(csvoutfile, delimiter='\t', quotechar='"')
        posteriorWriter.writerow(header)
        cityStates = posteriors.keys()
        cityStates.sort()
        for cityState in cityStates:
            row = [cityState, date]
            keys = posteriors[cityState].keys()
            keys.sort()
            for key in keys:
                try:
                    row += posteriors[cityState][key]
                except TypeError:
                        row += [None, None, None]
            posteriorWriter.writerow(map(str, row))
            
def getPosteriors():
    date_time_string = "2017-07-22_11" #Date time to get forecast data from.  Name of the directory.
    date_of_forecast = datetime.date(2017, 07, 22) #The date that the forecasts were sampled from.
    date_to_predict = datetime.date(2017, 07, 23) #The date to predict
    past_days = 5 #The number of prior days to use
    #Likelihood 
    weight_directory = "G:\School\VA Tech Courses\ZhangLab\DataIncubator\ForecastAdvisor\LastMonth"
    cities_location = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\LatLongCities.csv'
    data_directory = os.path.join("C:\Users\jsporter\Downloads\Data", date_time_string)
    output_directory = os.path.join("C:\Users\jsporter\Downloads\Temp", date_time_string)
    if not os.path.isdir(os.path.dirname(output_directory)):
        os.makedirs(os.path.dirname(output_directory))
    likelihood_location = os.path.join(output_directory, "Likelihoods_" + date_time_string + ".csv")
    all_forecasts_location = os.path.join(output_directory, "All_Forecasts_" + date_time_string)
    likelihoods = extractInfo.runExtractInfo(weight_directory, data_directory, cities_location, likelihood_location, all_forecasts_location, date_of_forecast)
    #Prior
    api_key_location = 'G:\School\VA Tech Courses\ZhangLab\DataIncubator\Weather_API_Keys.csv'
    prior_location = os.path.join(output_directory, "Priors_" + date_time_string + ".csv")
    history_directory = os.path.join(output_directory, "DarkSky_PriorData_" + date_time_string)    
    priors = getHistory.runGetHistory(api_key_location, cities_location, prior_location, history_directory, date_to_predict, past_days = past_days)
    #Posterior
    posterior_file = os.path.join(output_directory, "Posteriors_" + date_time_string + '.csv')
    cityDict = getForecasts.getCities(cities_location)
    #date_to_predict = datetime.date_to_predict(2017, 07, 21)
    cityStates = cityDict.keys()
    cityStates.sort()
    posteriors = {}
    for cityState in cityStates:
        posteriors[cityState] = computePosteriorArguments(likelihoods[cityState][date_to_predict], priors[cityState])
    pprint(posteriors)
    writePosteriorArguments(posteriors, posterior_file, date_to_predict)
    return posteriors
    
def main():
    getPosteriors()

if __name__ == "__main__":
    main()