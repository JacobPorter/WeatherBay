import requests
import os
from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

from .forms import CityForm

from scipy.stats import norm

import numpy as np

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.embed import components

def get_data(my_city):
    return None

def make_plot(my_city, data):
    x = np.linspace(-10,10,1000)
    pdf = norm.pdf(x, loc=2.5, scale=1.5)
    p1 = figure(title="Normal Distribution",tools="save",
                background_fill_color="#E8DDCB")
    p1.line(x, pdf, line_color="#D95B43", line_width=8, alpha=0.7, legend="PDF")
    p1.legend.location = "center_right"
    p1.legend.background_fill_color = "darkgrey"
    p1.xaxis.axis_label = 'x'
    p1.yaxis.axis_label = 'Pr(x)'
    return p1
    #show(gridplot(p1, ncols=2, plot_width=400, plot_height=400, toolbar_location=None))

def index(request):
    # if this is a POST request we need to process the form data
    script = ""
    div = ""
    data = None
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CityForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            my_city = form.cleaned_data['my_city']
            data = get_data(my_city)
            plot = make_plot(my_city, data)
            script, div = components(plot)
        else:
            my_city = ""
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CityForm()
        my_city = ""

    return render(request, 'index.html', {'form': form, 'my_city': my_city, 'script': script, 'div': div})

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

