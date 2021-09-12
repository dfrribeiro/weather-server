from stations.models import Station
from django.contrib.gis.db import models
#from django.contrib.postgres.fields.ranges import DateTimeRangeField
#from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import admin

SIGN_CHOICES = [
    ('lt', 'less than'),
    ('lte', 'less than or equal to'),
    ('eq', 'equal to'),
    ('gte', 'greater than or equal to'),
    ('gt', 'greater than'),
]

TYPE_CHOICES = [
    ("tmp", "Temperature"),
    ("hum", "Relative humidity"),
    ("atm", "Atmospheric pressure"),
    ("ws", "Wind speed"),
    ("wd", "Wind direction"),
    ("pre", "Precipitation"),
] # get from database?

class Event(models.Model):
    # automatic id primary key
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    measure_type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    condition_sign = models.CharField(max_length=32, choices=SIGN_CHOICES)
    condition_value = models.FloatField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    #is_active = models.BooleanField(default=True)

    #def get_absolute_url(self):
    #    return reverse('event-detail', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'events'

admin.site.register(Event)