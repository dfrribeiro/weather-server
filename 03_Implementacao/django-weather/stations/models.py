from datetime import datetime
import json
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.urls.base import reverse
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def update_filename(instance, filename):
    return instance.topic + "." + filename.split(".")[-1]

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Found at http://djangosnippets.org/snippets/976/
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

class Station(models.Model):
    topic = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=100)
    location = gis_models.PointField(geography=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    photo = models.ImageField(upload_to=update_filename, storage=OverwriteStorage(), null=True, blank=True)

    @property
    def get_absolute_url(self):
        return reverse('station-detail', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'stations'

    # json metadata - future upgrade TODO
    '''ts_name = models.CharField("Timestamp key", max_length=32)
    tmp_name = models.CharField("Temperature key", max_length=32)
    hum_name = models.CharField("Relative humidity key", max_length=32)
    atm_name = models.CharField("Atmospheric pressure key", max_length=32)
    ws_name = models.CharField("Wind speed key", max_length=32)
    wd_name = models.CharField("Wind direction key", max_length=32)
    rain_name = models.CharField("Precipitation key", max_length=32)'''
    # TODO add units

class MeasureManager(models.Manager):
    def register(self, station, data):
        if not Measure.objects.filter(station=station, data=data): # measure already exists, avoid duplicates
            measure = self.create(station=station, data=data)
        return measure

class Measure(models.Model):
    objects = MeasureManager()
    # automatic id
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    #timestamp = models.DateTimeField(auto_now=True) # received time
    data = models.JSONField(null=False) # has timestamp
    # pay attention to mqtt keepalive: it can run multiple searches

    @property
    def timestamp(self):
        return datetime.strptime(json.loads(self.data)["timestamp"], "%Y/%m/%d %H:%M:%S")
    
    #class Meta:
        #db_table = stations_measure
        #unique_together = (("station", "timestamp"),)

'''
JSON FORMAT = [
    ("timestamp", "Timestamp"),
    ("tmp", "Temperature"),
    ("hum", "Relative humidity"),
    ("atm", "Atmospheric pressure"),
    ("ws", "Wind speed"),
    ("wd", "Wind direction"),
    ("pre", "Precipitation"),
]
'''

admin.site.register(Station)
admin.site.register(Measure)