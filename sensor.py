
’’’
Copyright 2014 Sajid Nazir <nazirsajid@yahoo.com>

This file is part of WiseEye

WiseEye is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
’’’


#!/usr/bin/env python2.7
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


PIR_PIN = 7 #pin for PIR
RDR_SG_PIN = 27 #pin for xband radar signal (input)
RDR_EN_PIN = 22 #pin for enabling radar (output)
IRLED_PIN = 8 #pin for enabling IR LED panel
#TEMP_PIN = 4

def initGPIO():  #for setting pins (as input/output) other than PIR and Radar
    GPIO.setup(IRLED_PIN, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN) #output pin for IR LED



def activateIRLED():
    GPIO.output(IRLED_PIN, True) #enable the IRLED for night vision


def deactivateIRLED():
    GPIO.output(IRLED_PIN, False) #disable the IRLED


class Sensor():
    def __init__(self, pin, direction):
        self._sigPin = pin
        self._count = 0
        GPIO.setup(self._sigPin, GPIO.IN, pull_up_down= direction) #pin direction as GPIO.PUD_DOWN for PIR and GPIO.PUD_UP for radar
        print 'sensor constructor'
    def getTrigCount(self):
        return self._count #return the number of triggers
    def reset(self):
        self._count = 0
    def enableInterrupt(self, func):
        GPIO.add_event_detect(self._sigPin, GPIO.FALLING) #enable detection
        GPIO.add_event_callback(self._sigPin, func)
    def disableInterrupt(self, func):
        GPIO.remove_event_detect(self._sigPin)  


class PIR (Sensor):        
    def __init__(self, pin, direction):     #pin direction as GPIO.PUD_DOWN)
        Sensor.__init__(self, pin, direction)
       
    def callbackPIR(self, channel): #count the PIR activations
        self._count  = self._count + 1




class Radar(Sensor):
    def __init__(self, sPin, ePin, direction):     #pin direction as GPIO.PUD_UP)
        Sensor.__init__(self, sPin, direction)    
        self._enPin = ePin
        GPIO.setup(self._enPin, GPIO.OUT, pull_up_down= GPIO.PUD_DOWN)
      
    def disableRadar(self):
        GPIO.output(self._enPin, False) #disable the radar 
    def enableRadar(self):
        GPIO.output(self._enPin, True) #enable the radar 
    def callbackRadar(self, channel): #count the Radar activations
        self._count = self._count + 1






