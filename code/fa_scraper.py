
#http://www.forecastadvisor.com/Virginia/Blacksburg/24062/
import requests
import datetime
from bs4 import UnicodeDammit
from lxml import html
import time
import csv

state_translate = {
    'VA': 'Virginia',
    'FL': 'Florida',
    'NY': 'NewYork',
    'DC': 'DistrictofColumbia',
    'CA': 'California',
    'WA': 'Washington',
    'KS': 'Kansas',
    'IL': 'Illinois',
    'UT': 'Utah',
    'HI': 'Hawaii',
    'AK': 'Alaska',
    'TX': 'Texas',
    'FL': 'Florida',
    'MA': 'Massachusetts'
    }

def decode_html(html_string):
    converted = UnicodeDammit(html_string, is_html=True)
    #print str(converted)
    if not converted.unicode_markup:
        raise UnicodeDecodeError(
            "Failed to detect encoding, tried [%s]",
            ', '.join(converted.triedEncodings))
    # print converted.originalEncoding
    return converted.unicode_markup

def scrapeFA(city, state, zip_code):
    def get_accuracy(elements):
        start = True
        value_list = []
        a_dict = {}
        for element in elements:
            if element.xpath("@title"):
                if not start:
                    a_dict[value_list[0]] = tuple(value_list[1:len(value_list)])
                else:
                    start = False
                #services.append(element.xpath("@title")[0])
                value_list = [element.xpath("@title")[0]]
            else:
                value_list.append(float(element.text.replace('%', '')))
        a_dict[value_list[0]] = tuple(value_list[1:len(value_list)])
        return a_dict
    state = state_translate[state]
    city = city.replace("_", "")
    good_code = 200
    time_to_sleep = 1
    for _ in range(5):
        url_string = 'http://www.forecastadvisor.com/detail/%s/%s/%s/' % (state, city, zip_code)
        print(url_string)
        page = requests.get(url_string)
        #print(page.text)
        if page.status_code == good_code:
            break
        else:
            time.sleep(time_to_sleep)
            time_to_sleep *= 2
    tag_soup = page.text
    decoded = decode_html(tag_soup)
    root = html.fromstring(decoded)
    # 'Last Year'
    #first_month = root.xpath("//caption[contains(.,'Last Month')]")
    #last_month = root.xpath("//table[caption='Weather Forecast Accuracy Data Last Month']//td")
    last_month = root.xpath("//table[caption[contains(.,'Last Month')]]//td")
    #last_year = root.xpath("//table[caption='Weather Forecast Accuracy Data Last Year']//td")
    last_year = root.xpath("//table[caption[contains(.,'Last Year')]]//td")
    #print(first_month[0].text)
    #print([d.text for d in last_month])
    return {'Last Month': get_accuracy(last_month), 'Last Year': get_accuracy(last_year)}

def write_CSV(filename, a_dict):
    labels = ['Provider', 'High Temp', 'Low Temp', 'Icon Precip', 'Text Precip', 'Overall']
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='|')
        csvwriter.writerow(labels)
        for item in a_dict:
            csvwriter.writerow([item] + list(a_dict[item]))
            
def write_all(base_filename_month, base_filename_year, location_list):
    now = datetime.datetime.now()
    for city, state, zip_code in location_list:
        print("Starting with %s %s %s." % (city, state, zip_code))
        start = datetime.datetime.now()
        month_year = scrapeFA(city, state, zip_code)
        other_filename = city + state + zip_code + "_" + str(now.month) + "_" + str(now.year) + '.csv'
        write_CSV(base_filename_month + other_filename, month_year['Last Month'])
        write_CSV(base_filename_year + other_filename, month_year['Last Year'])
        finish = datetime.datetime.now()
        print("Finished with %s %s %s.  Took time:\t%s" % (city, state, zip_code, str(finish - start)))
        
        
def get_location_list(cities_filename):
    with open(cities_filename, 'r') as cities:
        csvreader = csv.reader(cities, delimiter='\t', quotechar='|')
        next(csvreader)
        return [(row[0], row[1], row[6]) for row in csvreader]      

if __name__ == '__main__':
    cities_filename = '/home/jsporter/workspace/WeatherBay/hello/static/LatLongCities.csv'
    filename_month = '/home/jsporter/workspace/WeatherBay/hello/static/Weights/Month/'
    filename_year = '/home/jsporter/workspace/WeatherBay/hello/static/Weights/Year/'
    write_all(filename_month, filename_year, get_location_list(cities_filename))
    #print(scrapeFA('Boston', 'MA', '02201'))


