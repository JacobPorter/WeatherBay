from django.db import models

class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)
# 
# cities = (
#     ('Blacksburg, VA', 'Blacksburg, VA'),
#     ('Boston, MA', 'Boston, MA'),
#     ('Chicago, IL', 'Chicago, IL'),
#     ('Honolulu, HI', 'Honolulu, HI'),
#     ('Houston, TX', 'Houston, TX'),
#     ('Juneau, AK', 'Juneau, AK'),
#     ('Lebanon, KS', 'Lebanon, KS'),
#     ('Miami, FL', 'Miami, FL'),
#     ('New York, NY', 'New York, NY'),
#     ('Salt Lake City, UT', 'Salt Lake City, UT'),
#     ('San Francisco, CA', 'San Francisco, CA'),
#     ('Seattle, WA', 'Seattle, WA'),
#     ('Tampa, FL', 'Tampa, FL'),
#     ('Washington, DC', 'Washington, DC')
#     )
# 
# class CityModel(models.Model):
#     my_city = models.CharField(choices = cities, max_length=14, default='Washington, DC')