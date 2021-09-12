import time
from machine import Pin, SoftI2C
from time import sleep
import ujson # vs pickle
import gc
import esp

from station import Station

# Sensors:
from BME280 import BME280
from anemo import Anemometer

esp.osdebug(None)
gc.collect()

with open("settings.json", "r") as f:
    config = ujson.loads(f.read())

mconf = config["mqtt"]
sta = Station(main_topic=mconf["main_topic"])

wconf = config["wlan"]
wlan = sta.connect_WLAN(ssid=wconf["ssid"], password=wconf["password"])
if wlan:
    print("Successfully connected to WLAN.")
else:
    print("Connection to WLAN failed...")

mqtt = sta.connect_MQTT(broker=mconf["broker"], port=mconf["port"], username=mconf["username"], password=mconf["password"])
#if mqtt:
#    print("Successfully connected to MQTT.")
#else:
#    print("Connection to MQTT failed...") is returning wrongly

bme = BME280(i2c=SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000))
sta.set_data_source('tmp', bme.temperature)
sta.set_data_source('hum', bme.humidity)
sta.set_data_source('atm', bme.pressure)

anemo = Anemometer(dig_pin=14, radius=.3)
sta.set_data_source('ws', anemo.speed)
#sta.set_data_source('wd', anemo.direction)

# pluvio = Pluviometer(i2c=SoftI2C(scl=Pin(?), sda=Pin(?), freq=10000))
# sta.set_data_source('rain', pluvio.precipitation)

# VEML6075
# TSL2561

while True:
    msg = sta.compile()
    print(msg)
    sta.publish_data(msg)
    time.sleep(60*5-11) # wait 5 minutes minus the 11 seconds it takes to calculate wind speed
