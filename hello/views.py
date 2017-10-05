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
from bokeh.plotting import figure
from bokeh.embed import components

#JS Callback stuff
from bokeh.models import CustomJS, ColumnDataSource, BoxSelectTool, Range1d, Rect, HoverTool

#output_file("boxselecttool_callback.html")

# area = Area(x='x',
#         y='y',
#         width='width',
#         height='height',
#         fill_alpha=0.3,
#         fill_color='#009933')

def determine_icon_size(s, d):
    if d == 1:
        return 64
    elif d == 2:
        return 91
    elif d == 3:
        return 111
    elif d == 4:
        return 128
#     if d == 1:
#         return s
#     discriminant = math.sqrt(math.pow(s * 2, 2) - 4 * (math.pow(s, 2) * (1-d)))
#     thing = max(-2*s + discriminant, -2*s - discriminant)
#     return int(thing / 2.0)

def make_pdf_plot(title, data, label = 'Temperature', pdf_function = norm):
    x_length = 10000
    if pdf_function == norm:
        upper = data[1] + (data[2] * 5) #max(data[1] + 1,
        lower = data[1] - (data[2] * 5) #min(data[1] - 1, data[1] - (data[2] * 5))
    elif pdf_function == beta:
        upper = 1
        lower = 0
    else: #Gamma
        lower = 0
        upper = 1.5
    step_size = (upper - lower) / x_length
    x = np.linspace(lower,upper,x_length)
    if pdf_function == gamma:
        pdf = pdf_function.pdf(x, data[1], scale = data[2])
        cdf = pdf_function.cdf(x, data[1], scale = data[2])
    else:
        pdf = pdf_function.pdf(x, data[1], data[2])
        cdf = pdf_function.cdf(x, data[1], data[2])
    if pdf_function != norm:
        maximizer = lower + step_size * np.argmax(pdf)
    else:
        maximizer = data[1]
    source = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[], prob=[], x0=[], x1=[]))
    cdf = ColumnDataSource(data=dict(cdf=cdf))
    bounds = ColumnDataSource(data=dict(upper=[upper], lower=[lower], step=[step_size]))
    #prob = ColumnDataSource(data=dict(prob=[0.0]))
    
    callback = CustomJS(args=dict(source=source, cdf=cdf, bounds=bounds), code="""
            // get data source from Callback args
            var data = source.data;
            var cdf = cdf.data['cdf'];
            //var prob = prob.data;
            /// get BoxSelectTool dimensions from cb_data parameter of Callback
            var geometry = cb_data['geometry'];
            /// calculate Rect attributes
            var x1 = geometry['x1']
            var x0 = geometry['x0']
            var width = geometry['x1'] - geometry['x0'];
            var height = geometry['y1'] - geometry['y0'];
            var x = geometry['x0'] + width/2;
            //var y = geometry['y0'] + height/2;
            var y = 0 + height/2;
            var cdf1 = 0;
            var cdf2 = 0;
            var upper = bounds.data['upper'][0];
            var lower = bounds.data['lower'][0];
            var step = bounds.data['step'][0];
            if (x0 >= upper) {
                var cdf0 = cdf[9999];
            } else if (x0 <= lower) {
                var cdf0 = cdf[0];
            } else {
                var cdf0 = cdf[Math.round((x0 - lower) / step)];
            }
            if (x1 >= upper) {
                var cdf1 = cdf[9999];
            } else if (x1 <= lower) {
                var cdf1 = cdf[0];
            } else {
                var cdf1 = cdf[Math.round((x1 - lower) / step)];
            }
            /// update data source with new Rect attributes
            data['x'].pop();
            data['y'].pop();
            data['width'].pop();
            data['height'].pop();
            data['x'].push(x);
            data['y'].push(y);
            data['width'].push(width);
            data['height'].push(height);
            data['prob'].pop();
            data['prob'].push(cdf1 - cdf0);
            data['x0'].pop();
            data['x1'].pop();
            data['x0'].push(x0)
            data['x1'].push(x1)
            // emit update of data source
            source.change.emit();
        """)
    
    box_select = BoxSelectTool(callback=callback, dimensions="width")
    hover = HoverTool(tooltips=[
        ("Prob", "@prob"),
        ("(x0,x1)", "(@x0, @x1)"),
    ])
    rect = Rect(x='x',
                y='y',
                width='width',
                height='height',
                #tags=['cdf', cdf],
                fill_alpha=0.3,
                fill_color='#009933')
    
    title = "%s: %f" % (title, maximizer)
    p1 = figure(title=title,tools="wheel_zoom,pan,reset,save",
                background_fill_color="#E8DDCB", toolbar_location="right")
    p1.add_tools(box_select)
    p1.add_tools(hover)
    p1.toolbar.active_drag = box_select
    p1.line(x, pdf, line_color="#D95B43", line_width=8, alpha=0.7)#legend="PDF")
    p1.legend.location = "center_right"
    p1.legend.background_fill_color = "darkgrey"
    p1.xaxis.axis_label = label
    p1.yaxis.axis_label = 'Density' #'Pr(' + label +  ')'
    p1.add_glyph(source, rect, selection_glyph=rect, nonselection_glyph=rect)
    return p1

def make_gridplot(p1, p2, p3, p4):
    return gridplot(p1,p2,p3,p4, ncols=4, plot_width=400, plot_height=400, toolbar_location="below")

def index(request):
    # if this is a POST request we need to process the form data
    script = ''
    div = ''
    icons = []
    forecast_date_string = ""
#     script_min = ""
#     div_min = ""
#     script_max = ""
#     div_max = ""
    icon_weight_base = 64
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
            icons = [(icon, determine_icon_size(icon_weight_base, posterior_dict['icon'][1][icon]))  for icon in icon_search_order if posterior_dict['icon'][1][icon] > 0]
            icons.sort(key=lambda x: -x[1])
            new_gamma = list(posterior_dict['precipAmount'])
            new_gamma[2] = 1 / new_gamma[2]
            plot_max = make_pdf_plot('Maximum Temperature', posterior_dict['temperatureMax'], 'Max Temperature', norm)
            plot_min = make_pdf_plot('Minimum Temperature', posterior_dict['temperatureMin'], 'Min Temperature', norm)
            plot_pprob = make_pdf_plot('Precipitation Probability', posterior_dict['precipProbability'], 'Precipitation probability', beta)
            plot_pamt = make_pdf_plot('Precipitation Amount', new_gamma, 'Precipitation amount', gamma)
            script, div = components(make_gridplot(plot_max, plot_min, plot_pprob, plot_pamt))
            print(datetime.datetime.now())
            prediction_date = datetime.datetime.now() + datetime.timedelta(days = 1)
            prediction_date = datetime.date(prediction_date.year, prediction_date.month, prediction_date.day)
            forecast_date_string = 'The weather on %s is predicted to be the following.' % (prediction_date)
            forecast_date_string = 'The weather forecast for tomorrow is predicted to be the following.'
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
    
    render_dictionary = {'forecast_date': forecast_date_string, 
                         'form': form, 
                         'my_city': my_city, 
                         'post_dict':str(posterior_dict), 
                         'script':script, 
                         'div':div
                         }
    for i, icon_weight in enumerate(icons):
        icon, weight = icon_weight
        render_dictionary['icon' + str(i + 1)] = icon
        render_dictionary['iw_' + str(i + 1)] = weight
    return render(request, 'index.html', render_dictionary)

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

# if __name__ == "__main__":
#     print(getWebForecasts.strNow())
    
    