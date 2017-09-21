import requests
import os
from collections import defaultdict
from .getWebForecasts import *
from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

from .forms import CityForm

from scipy.stats import norm
from scipy.stats import beta
from scipy.stats import gamma

import numpy as np

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.embed import components



def make_normal_plot(my_city, title, data):
    upper = int(data[1] + data[2] * 5)
    lower = int(data[1] - data[2] * 5)
    x = np.linspace(lower,upper,1000)
    pdf = norm.pdf(x, loc=data[1], scale=data[2])
    p1 = figure(title=title,tools="save",
                background_fill_color="#E8DDCB")
    p1.line(x, pdf, line_color="#D95B43", line_width=8, alpha=0.7, legend="PDF")
    p1.legend.location = "center_right"
    p1.legend.background_fill_color = "darkgrey"
    p1.xaxis.axis_label = 'Temperature'
    p1.yaxis.axis_label = 'Pr(Temperature)'
    return p1
    #show(gridplot(p1, ncols=2, plot_width=400, plot_height=400, toolbar_location=None))

def make_gridplot(p1, p2):
    return gridplot(p1,p2, ncols=2, plot_width=400, plot_height=400, toolbar_location=None)

def index(request):
    # if this is a POST request we need to process the form data
    script = ''
    div = ''
    script_min = ""
    div_min = ""
    script_max = ""
    div_max = ""
    icon1 = ''
    icon2 = ''
    icon3 = ''
    city_dictionary = getCities('./hello/static/LatLongCities.csv')
    api_key_dictionary = get_API_keys()
    weight_dictionary = getAllWeights(city_dictionary.keys(), './hello/static/Weights/')
    #print("Got past the weights")
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CityForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            my_city = cleanInput(form.cleaned_data['my_city']).replace("_", " ")
            posterior_dict =  get_forecasts(my_city, city_dictionary, api_key_dictionary, weight_dictionary)
            for icon in icon_search_order:
                amount = posterior_dict['icon'][1][icon]
                if 2 == amount:
                    icon1 = icon
                elif 1 == amount and icon2 == '':
                    icon2 = icon
                elif 1 == amount:
                    icon3 = icon
            plot_max = make_normal_plot(my_city, 'Maximum temperature', posterior_dict['temperatureMax'])
            plot_min = make_normal_plot(my_city, 'Minimum temperature', posterior_dict['temperatureMin'])
            script, div = components(make_gridplot(plot_max, plot_min))
            #script_max, div_max = components(plot_max)
            #script_min, div_min = components(plot_min)
        else:
            my_city = ""
            posterior_dict = ""
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CityForm()
        my_city = ""
        posterior_dict = ""
        #'script_max': script_max, 'div_max': div_max, 'script_min': script_min, 'div_min': div_min
    return render(request, 'index.html', {'form': form, 'my_city': my_city, 'post_dict':str(posterior_dict), 'script':script, 'div':div, 'icon1':icon1, 'icon2':icon2, 'icon3':icon3})

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

# if __name__ == "__main__":
#     print(getWebForecasts.strNow())
    
    