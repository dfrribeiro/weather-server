from time import time_ns
from machine import Pin, ADC
import math

class Anemometer:

    def __init__(self, dig_pin, adc_pin=None, radius=.3, min_delay=20000000):
        self._dig_pin = Pin(dig_pin, Pin.IN)
        self._radius = radius # meters
        self._min_delay = min_delay #math.pi*self._radius/70. # nanoseconds (70 m/s max)
        print("Min delay: " + str(self._min_delay/1e6) + " ms")

        if adc_pin:
            self._adc_pin = Pin(adc_pin)
            self._adc_dir = ADC(self._adc_pin)
            self._adc_dir.atten(ADC.ATTN_11DB)
        
        self.half_rotations = 0
        self._last_event_time = time_ns()
        self._wind_speed = 0
        self._dig_pin.irq(trigger=Pin.IRQ_RISING, handler=self._handle_interrupt)

    def _handle_interrupt(self, pin):
        aux = time_ns()
        dtime = aux - self._last_event_time
        if dtime > self._min_delay:
            self.half_rotations += 1
            self._last_event_time = aux

    def _measure_rps(self, secs=10):
        rot_start = self.half_rotations
        start = time_ns()
        while True:
            if time_ns() - start > secs*1e9:
                rot_end = self.half_rotations
                r = (rot_end - rot_start)/2
                rps = r / secs
                print("Registered "+str(r)+" rotations in "+str(secs)+" secs ("+str(rps)+" rps).")
                return rps

    #@property
    def speed(self):
        rps = self._measure_rps()
        #dtime = 1./rps if rps else 0
        w = 2*math.pi * rps # angular velocity
        v = w * self._radius # linear velocity
        
        # Convert to kmh
        s = v * 3.6
        #si = s // 100
        #sd = s - si * 100
        #return "{}.{:02d}km/h".format(si, sd)
        return s

    #@property
    def direction(self):
        wind_direction = self._adc_dir.read() # VP = 36 VN = 39
        wd = wind_direction * 359 / 3095 + 359
        #wdi = wd // 100
        #wdd = wd - wdi * 100
        #return "{}.{:02d}°".format(wdi, wdd)
        return wd

if __name__=='__main__':
    an = Anemometer(dig_pin=14, radius=0.36)

    while True:
        print(an.speed)
        #print(an.direction)