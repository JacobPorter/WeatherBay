from django import forms

class CityForm(forms.Form):
    my_city = forms.CharField(label='City', max_length=100)
