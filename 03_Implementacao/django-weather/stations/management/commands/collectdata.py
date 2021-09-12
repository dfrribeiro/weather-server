from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import paho.mqtt.client as mqtt
import json
from stations.models import Station, Measure
from events.models import Event
from datetime import datetime
from threading import Thread

class Command(BaseCommand):
    help = 'Collects data from MQTT brokers'
    available_brokers = [{'address': "cjsg.ddns.net", 'username': "meteo", 'password': "iselmeteo"}] # opt. port/keepalive

    def handle(self, *args, **options):
        # One thread for each broker
        for server in self.available_brokers:
            #collect_data(server)
            Thread(target=self.collect_data, args=(server, )).start()

    def on_connect(self, client, userdata, rc, properties=None):
        client.subscribe("weather/#") # any topic under weather
        self.stdout.write("Connected and subscribed")

    def on_message(self, client, userdata, msg):
        pk = msg.topic.split("/")[-1]
        measure = msg.payload.decode()
        Measure.objects.register(station=Station.objects.get(topic=pk), data=measure)
        self.stdout.write("New measure registered from " + pk)

        obj = json.loads(measure)
        for type in obj.keys():
            # check type
            event_list = Event.objects.filter(station=Station.objects.get(topic=pk), measure_type=type)

            for ev in event_list:
                # check condition
                sign = ev.condition_sign
                condition = False
                value = float(obj[type])
                if sign == 'lt':
                    condition = value < ev.condition_value
                elif sign == 'lte':
                    condition = value <= ev.condition_value
                elif sign == 'eq':
                    condition = value == ev.condition_value
                elif sign == 'gte':
                    condition = value >= ev.condition_value
                elif sign == 'gt':
                    condition = value > ev.condition_value

                # check time slot
                if ev.time_start < datetime.now().time() < ev.time_end and condition:
                    send_event_mail(ev)
                    self.stdout.write("Notified " + ev.creator.username + " of event")

    def collect_data(self, broker):
        client = mqtt.Client()
        
        un = broker.get('username')
        if un:
            client.username_pw_set(un, password=broker.get('password'))

        client.on_message = self.on_message
        client.on_connect = self.on_connect
        client.connect(broker.get('address'), port=broker.get('port') or 1883, keepalive=broker.get('keepalive') or 60)

        client.loop_forever()

# static independent function
def send_event_mail(ev):
    mail_subject = 'WSM Event Notification'
    message = render_to_string('events/event_triggered.html', {'event': ev,})
    email = EmailMessage(
                mail_subject, message, to=[ev.creator.email]
    )
    email.send()