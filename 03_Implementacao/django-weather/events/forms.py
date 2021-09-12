from django import forms
from .models import Event
from stations.models import Station

class EventForm(forms.ModelForm):

        def __init__(self, *args, **kwargs):
                user = kwargs.pop('user')

                super(EventForm, self).__init__(*args, **kwargs)
                self.fields['station'].queryset=Station.objects.filter(owner=user.id)
                self.creator = user

                input_classes = "text-gray-800 block w-full px-4 py-3 mb-4 border border-transparent border-gray-200 rounded-lg focus:ring focus:ring-indigo-400 focus:outline-none"
                self.fields['station'].widget.attrs['class'] = \
                                self.fields['measure_type'].widget.attrs['class'] = \
                                        self.fields['condition_sign'].widget.attrs['class'] = \
                                                self.fields['condition_value'].widget.attrs['class'] = \
                                                        self.fields['time_start'].widget.attrs['class'] = \
                                                                self.fields['time_end'].widget.attrs['class'] = input_classes          

        class Meta:
                fields = ['station', 'measure_type', 'condition_sign', 'condition_value', 'time_start', 'time_end']
                model = Event
                widgets = {'time_start': forms.TimeInput(attrs={'type': 'time'}), 'time_end': forms.TimeInput(attrs={'type': 'time'})}
