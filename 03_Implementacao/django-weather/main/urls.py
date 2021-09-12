"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as a
from stations import views as s
from events import views as e

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', s.home, name='home'), # all stations
    path('accounts/login/', a.UpdatedLoginView.as_view(), name='login'),
    path('accounts/logout/', a.logout, name='logout'),
    #path('accounts/password_reset/', a.password_reset, name='password-reset'),
    path('accounts/signup/', a.signup, name='signup'),
    path('accounts/activate/<uidb64>/<token>/', a.activate, name='activate'),
    path('events/', e.event_list, name='event-list'),
    path('events/add/', e.EventCreateView.as_view(), name='event-add'),
    path('events/<int:pk>/update/', e.EventUpdateView.as_view(), name='event-update'),
    path('events/<int:pk>/delete/', e.EventDeleteView.as_view(), name='event-delete'),
    path('stations/', s.station_list, name='station-list'),
    path('stations/search/', s.station_search, name='station-search'),
    path('stations/add/', s.StationCreateView.as_view(), name='station-add'),
    path('stations/<str:pk>/', s.StationDetailView.as_view(), name='station-detail'),
    path('stations/<str:pk>/update/', s.StationUpdateView.as_view(), name='station-update'),
    path('stations/<str:pk>/delete/', s.StationDeleteView.as_view(), name='station-delete'),
    path('get_user_location', s.get_user_location, name='get_user_location'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()