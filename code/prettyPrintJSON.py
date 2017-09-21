import pprint
import json
import sys
import os

directory = "G:\School\VA Tech Courses\ZhangLab\DataIncubator\Data\\2017-07-20-23"
#file_name = "AccuWeather_BlacksburgVA_2017-07-20_23-49-10_5day.json" #Number
file_name = "DarkSky_BlacksburgVA_2017-07-20_23-39-15_latlon.json" #text

#file_name = "NWS_BlacksburgVA_2017-07-20_23-29-27_forecast.json" # Use text
#file_name = "NWS_BlacksburgVA_2017-07-20_23-29-27_grid.json"

#file_name = "WUnderground_BlacksburgVA_2017-07-20_23-54-17_forecast.json"

file_location = os.path.join(directory, file_name)
output = sys.stdout
#output = open("pprint_test.txt", 'w')
with open(file_location, 'r') as printMe:
    forecast_data = json.load(printMe)
    pprint.pprint(forecast_data, output)