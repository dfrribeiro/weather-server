from django import forms
from .models import Station

'''
# Creating a form to add an article.
form = ArticleForm()

# Creating a form to change an existing article.
article = Article.objects.get(pk=1)
form = ArticleForm(instance=article)
'''

from .ids import name_to_topic
from django import forms
from django.contrib.gis import forms as gis_forms

class StationForm(forms.ModelForm):

    class Meta:
        input_classes = "text-gray-800 block w-full px-4 py-3 mb-4 border border-transparent border-gray-200 rounded-lg focus:ring focus:ring-indigo-400 focus:outline-none"
        model = Station
        fields = ['name', 'location', 'photo', 'description']
        widgets = {"name": forms.TextInput(attrs={'placeholder': "Station name", 'class': input_classes}),
                   "location": gis_forms.OSMWidget(attrs={'map_width': 300, 'map_height': 300, 'default_lat': 38.7561, 'default_lon': -9.1169, 'default_zoom': 5}),
                   "photo": forms.ClearableFileInput(attrs={'class': input_classes, 'accept': "image/*", 'style': "color: rgb(229, 231, 235)"}),
                   "description": forms.Textarea(attrs={'placeholder': "Description (optional)", 'class': input_classes})}

    #def __init__(self, *args, **kwargs):
        #super(StationForm, self).__init__(*args, **kwargs)
        #self.fields['location'].required = self.fields['photo'].required = False

    def save(self, commit=True):
        obj = super(forms.ModelForm, self).save(commit=False)
        obj.topic = name_to_topic(obj.name, previous=obj.topic)
        # obj.owner
        if commit:
            obj.save()
        return obj
