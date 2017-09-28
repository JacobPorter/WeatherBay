from django import forms

# class CityForm(forms.Form):
#     my_city = forms.CharField(label='City', max_length=100)

cities = (
    ('Blacksburg, VA', 'Blacksburg, VA'),
    ('Boston, MA', 'Boston, MA'),
    ('Chicago, IL', 'Chicago, IL'),
    ('Honolulu, HI', 'Honolulu, HI'),
    ('Houston, TX', 'Houston, TX'),
    ('Juneau, AK', 'Juneau, AK'),
    ('Lebanon, KS', 'Lebanon, KS'),
    ('Miami, FL', 'Miami, FL'),
    ('New York, NY', 'New York, NY'),
    ('Salt Lake City, UT', 'Salt Lake City, UT'),
    ('San Francisco, CA', 'San Francisco, CA'),
    ('Seattle, WA', 'Seattle, WA'),
    ('Tampa, FL', 'Tampa, FL'),
    ('Washington, DC', 'Washington, DC')
    )

class CityForm(forms.Form):
    my_city = forms.CharField(label = 'City', max_length=30,
                widget=forms.Select(choices=cities))