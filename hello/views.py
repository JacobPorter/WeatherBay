import requests
import os
from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

from .forms import CityForm

def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CityForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            my_city = form.cleaned_data['my_city']
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

    return render(request, 'index.html', {'form': form, 'my_city': my_city})

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

