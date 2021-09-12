from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Event
from .forms import EventForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

@login_required
def event_list(request):
    event_list = Event.objects.filter(creator=request.user)
    
    context = {
        'events': event_list,
    }
    return render(request, 'events/event_list.html', context)

@method_decorator(login_required, name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('event-list')

    def get_form_kwargs(self):
        kwargs = super(EventCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

@method_decorator(login_required, name='dispatch')
class EventUpdateView(UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('event-list')

    def get_form_kwargs(self):
        kwargs = super(EventUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs
    
    def test_func(self):
        user = self.request.user
        return user == self.get_object().creator or user.is_staff

@method_decorator(login_required, name='dispatch')
class EventDeleteView(UserPassesTestMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('event-list')

    def test_func(self):
        user = self.request.user
        return user == self.get_object().creator or user.is_staff