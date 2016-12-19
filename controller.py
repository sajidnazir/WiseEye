
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

from sensor import * 
from image import * 
import os 
import csv
import Adafruit_DHT
import sys

class Controller():
    def __init__(self):        #class initialization
        initGPIO()
        self._param = []       #create an empty list
        self._timeBetweenImages = None #initilaized on reading the config file
        self._readConfigFile() #populate param from configuration file
                               #assign values from config file
        self._pimg = ImageProcessor()
        self._pir = PIR(PIR_PIN, GPIO.PUD_DOWN )
        self._xbr = Radar(RDR_SG_PIN, RDR_EN_PIN, GPIO.PUD_UP)
        self._myfile = open('captureData.csv','a')
        self._wrtr = csv.writer(self._myfile)
        self._wrtr.writerow(["Serial","Image","Brightness","Threshold", "PIR Count","Radar Count","No of Blobs","Largest Blob Size","verdict"])
        self._ser = 1  

    def __del__(self):             #class destructor
        pass
  
    def _readConfigFile(self):
        idx = 0
        with open('config.txt') as fp:
            for line in fp:
                line = line.partition(':')[2]
                print line
                self._param.insert(idx, int(line.rstrip()) )
                idx = idx + 1
            #print "index", idx
            self._timeBetweenImages = self._param[0]
            #print 'param', self._param[0]
            #for x  in range(0, idx):
            #    print self._param[x]*2
   
    def run(self):
        initGPIO()  #set the pins except for radar, and pir
        print 'initializing ...'
        time.sleep(2)
        self._pimg.takePicture('static')
        CAP_PIC = False
        self._xbr.enableRadar()
        
        while(1):
            self._xbr.enableInterrupt(self._xbr.callbackRadar)
            self._pir.enableInterrupt(self._pir.callbackPIR) #start listening for activations
            time.sleep(0.05) #sleep for 50 ms
            self._pir.disableInterrupt(self._pir.callbackPIR)

            if ( self._pir.getTrigCount() > 0):   #motion detected by PIR
                start = time.time()
                self._pimg.takePicture('motion')
                p1,p2,p3,p4,p5,p6=self._pimg.writeImageStats()
                self._xbr.disableInterrupt(self._xbr.callbackRadar)  #to accumulate Radar triggers longer than for PIR


                self._wrtr.writerow([self._ser, p1, p2,p3,self._pir.getTrigCount(),self._xbr.getTrigCount(),p4, p5, p6])
                self._myfile.flush()
                
                self._ser = self._ser + 1
               
                timeToSleep  =  self._timeBetweenImages  - (time.time()-start)
                print 'Sleeping for ',timeToSleep
                time.sleep(timeToSleep)
                
            else:
                lapse = time.strftime('%M')
                if((CAP_PIC == False) and ((int(lapse))%2 == 0) ):
                    CAP_PIC = True
                    #print "time lapse"
                 
                    self._pimg.calculateBrightness() #a n image without IR LEDs
                    self._pimg.takePicture('static')
                    
                elif (int (lapse) % 2 != 0):
                    CAP_PIC = False
                #self._xbr.disableRadar()   #disable radar for the next round
                self._xbr.disableInterrupt(self._xbr.callbackRadar)  #execute else:
            self._xbr.reset()   #execute while(1)
            self._pir.reset()



def main():
    con = Controller()
    con.run()

if  __name__ =='__main__':
    main()
