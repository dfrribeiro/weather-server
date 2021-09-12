# MQTT Client
import network
from umqttsimple import MQTTClient
import machine
import ujson
import ubinascii

import ntptime
import time

class Station(MQTTClient):
    # Singleton
    def __init__(self, main_topic="station"):
        super().__init__(ubinascii.hexlify(machine.unique_id()))

        self.main_topic = main_topic
        self._data = {}
        #print("Station initialized.")

        #super().connect()
        self._sta_if = None
    
    def publish_data(self, msg):
        ''' Publishes message to main topic
        '''
        ret = super().publish(topic=self.main_topic, msg=msg, qos=1, retain=True)
        #if ret:
        #    print("Message published to broker.")
        #else:
        #    print("Message failed to reach broker.")
        return ret

    def connect_MQTT(self, broker="localhost", port=1883, username=None, password=None):
        ''' Initializes connection to MQTT broker'''
        self.server = broker
        self.port = port
        if username is not None:
            self.user = username
            self.pswd = password
        return super().connect(clean_session=True)
    
    def connect_WLAN(self, ssid=None, password=""):
        '''Initializes a WLAN internet connection.\n
           If the SSID isn't given as argument, it scans for available networks
           and prompts the user to input SSID and password.\n
           Note: does not support WPA2-Enterprise.
           Returns the state of the connection.'''
        self._sta_if = network.WLAN(network.STA_IF)
        self._sta_if.active(True)
        if ssid is None:
            print("Available WLAN: " + str(self._sta_if.scan()))
            ssid = input("SSID: ")
            password = input("Password: ")
        self._sta_if.connect(ssid, password)
        self.__sync_NTP()
        return self._sta_if.isconnected()
    
    def __sync_NTP(self, host="pool.ntp.org"):
        ntptime.host = host
        try:
            print("Local time before synchronization：%s" %str(time.localtime()))
            ntptime.settime()
            print("Local time after synchronization：%s" %str(time.localtime()))
        except:
            print("Error syncing time")

    def set_data_source(self, abbr, source):
        '''Stores the sensor's function for future reading
           of whatever measure abbr abbreviates.\n
           Returns the first reading attempt, None if it failed.'''
        self._data[abbr] = source
        if source:
            return source()
    
    def format_time(self, time_tuple):
        return "%4d/%02d/%02d %02d:%02d:%02d" % time_tuple[:6]

    def compile(self):
        '''Returns a timestamped dictionary with the latest readings.\n
           Refer to "settings.json" for the keys' names.'''
        res = {key:str(fun()) for key,fun in self._data.items() if fun is not None}
        res["timestamp"] = self.format_time(time.localtime())
        return ujson.dumps(res)