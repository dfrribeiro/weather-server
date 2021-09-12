from django.contrib.gis.measure import D
from django.db.models.fields import DateTimeField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.auth.decorators import login_required
from .forms import StationForm
from .models import Station, Measure
from django.utils.decorators import method_decorator
from django.contrib.gis.db.models.functions import Distance
from django.contrib.auth.mixins import UserPassesTestMixin
import requests
from django.db.models import Q
from tzwhere import tzwhere
from datetime import datetime, timedelta
from dateutil import tz
import json
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models.functions import Cast

g = GeoIP2()

def __get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_location(request):
    try:
        ip_address = __get_client_ip(request)
        lat, lon = g.lat_lon(ip_address)
        response = { 'lat': lat, 'lon': lon }
        return JsonResponse(response)
    except:
        return JsonResponse({ 'lat': '??', 'lon': '??' })

def home(request):
    '''Closest 20 stations'''
    try:
        ip_address = __get_client_ip(request)
        pnt = g.geos(ip_address)
        station_list = Station.objects.annotate(distance=Distance('location', pnt)).order_by('distance')[:20]
        for sta in station_list:
            value = float(str(sta.distance).split(" ")[0])
            sta.distance = D(m=value).km
    except:
        station_list = Station.objects.order_by("topic")[:20]
    
    context = {
        'stations': station_list,
    }
    return render(request, 'stations/home.html', context)

def station_search(request):
    if 'query' in request.GET:
        query_term = request.GET['query']
        combined_queryset = Station.objects.filter(Q(topic__icontains=query_term) | Q(name__icontains=query_term) | Q(owner__username__icontains=query_term))

        try:
            ip_address = __get_client_ip(request)
            pnt = g.geos(ip_address)
            station_list = combined_queryset.annotate(distance=Distance('location', pnt)).order_by('distance')
            for sta in station_list:
                value = float(str(sta.distance).split(" ")[0])
                sta.distance = D(m=value).km
        except:
            station_list = combined_queryset.order_by('topic')
        
        context = {
            'stations': station_list,
        }
        return render(request, 'stations/home.html', context)
    return redirect('home')

@login_required
def station_list(request):
    '''Only authenticated user's stations, but no limit'''
    try:
        ip_address = __get_client_ip(request)
        pnt = g.geos(ip_address)
        station_list = Station.objects.filter(owner=request.user).annotate(distance=Distance('location', pnt)).order_by('distance')
        for sta in station_list:
            value = float(str(sta.distance).split(" ")[0])
            sta.distance = D(m=value).km
    except:
        station_list = Station.objects.filter(owner=request.user).order_by("location")
    
    context = {
        'stations': station_list,
    }
    return render(request, 'stations/station_list.html', context)

class StationDetailView(DetailView):
    model = Station
    template_name = 'stations/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lon, lat = self.get_object().location

        # LOCAL DATE GET
        tzw = tzwhere.tzwhere()
        local_time = datetime.now(tz.gettz(tzw.tzNameAt(lat, lon)))
        next_midnight = datetime.combine(local_time, datetime.max.time()) + timedelta.resolution
        millis_until = (next_midnight.timestamp() - local_time.timestamp()) * 1000
        context['tzOffset'] = local_time.utcoffset().seconds/3600 #.timestamp() * 1000
        context['untilMidnight'] = millis_until

        # CITY/COUNTRY GET
        url = 'https://api.bigdatacloud.net/data/reverse-geocode-client'
        params = {'latitude': lat, 'longitude': lon, 'localityLanguage': "en"}
        r = requests.get(url, params=params)
        result = r.json()
        context['city'] = result['locality']
        context['country'] = result['countryCode']

        measure_list = Measure.objects.filter(station=self.get_object())#.order_by('-id') select_related?
        measure_list = sorted(measure_list, key=lambda a: a.timestamp, reverse=True)
        context['measures'] = measure_list
        
        return context

@method_decorator(login_required, name='dispatch')
class StationCreateView(CreateView):
    model = Station
    success_url = reverse_lazy('station-list')
    form_class = StationForm
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return redirect(self.success_url)

@method_decorator(login_required, name='dispatch')
class StationUpdateView(UserPassesTestMixin, UpdateView):
    model = Station
    form_class = StationForm

    def test_func(self):
        user = self.request.user
        return user == self.get_object().owner or user.is_staff
    
    def get_success_url(self, **kwargs):    
        return self.get_object().get_absolute_url

@method_decorator(login_required, name='dispatch')
class StationDeleteView(UserPassesTestMixin, DeleteView):
    model = Station
    success_url = reverse_lazy('station-list')
    template_name = "stations/delete.html"

    def test_func(self):
        user = self.request.user
        return user == self.get_object().owner or user.is_staff