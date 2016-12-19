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

from PIL import Image, ImageStat
from scipy import ndimage
import time
import datetime
import math, operator
import os
import subprocess
import cv2
import cv2.cv as cv
import numpy as np
from shutil import copyfile
import picamera

from sensor import *
import threading

class ImageProcessor():
    def __init__(self):
        self._prevImg = None
        self._currImg = None
        self._brightness = 100 #initially consider it daylight
        self._brightness_threshold = 15 #lower values to be considered dark
        self._time = None #time for the image capture 
        self._RPIcam = picamera.PiCamera()
        self._RPIcam.resolution = (640, 480) #set the camera resolution here
        self._RPIcam.led = False     #switch off camera LED
        print 'image constructor'
    def __del__(self):
        self._RPIcam.close()
  
    def takePicture(self, type): 
        self._time = datetime.datetime.now()
        timeStamp = self._time.strftime('%Y%m%d-%H%M%S')     
        if self._brightness <= self._brightness_threshold:  #its dark
            activateIRLED()#switch-on the IR LEDs
        if type == 'static':
            imgName = timeStamp + '-static.jpg'
            self._RPIcam.capture(imgName)
            self._prevImg = cv2.imread(imgName)
        else: 
            imgName = timeStamp + '.jpg'
            self._RPIcam.capture(imgName)
            self._currImg = cv2.imread(imgName)
        deactivateIRLED()#switch off the IR LEDs
   

    def calculateBrightness(self):
        self._RPIcam.capture("refImg.jpg")
        im = Image.open("refImg.jpg").convert('L')
        stat = ImageStat.Stat(im)
        self._brightness = (int)(((100-0)*(stat.rms[0] - 0))/(255-0)) + 0 #scales a no from min (0 black) to max (255 white) range to 0-100 
        

    def writeImageStats(self):
        #extract ROIs
        ROI_P = self._prevImg[190:460, 20:620]
        roipImgName = self._time.strftime('%Y%m%d-%H%M%S-') + 'roi_static.jpg'
        cv2.imwrite(roipImgName, ROI_P)
        ROI_C = self._currImg[190:460, 20:620]
        roicImgName = self._time.strftime('%Y%m%d-%H%M%S-') + 'roi_motion.jpg'
        cv2.imwrite(roicImgName, ROI_C)
        #compute a difference image on ROIs
        grayp = cv2.cvtColor(ROI_P, cv2.COLOR_BGR2GRAY)  # for calculating difference image
        grayc  = cv2.cvtColor(ROI_C, cv2.COLOR_BGR2GRAY)   # for calculating difference image

        diff = cv2.absdiff(grayc, grayp)
        otsu, diff_b = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)
        print 'threshold by otsu', otsu
        thresh = round((otsu+self._brightness)/2.0)
        print 'thresh', thresh
        ret, diff_b = cv2.threshold(diff, thresh, 255, cv2.THRESH_BINARY)

        kernel = np.ones((3,3),np.uint8)  #erosion
        diff_erosion = cv2.erode(diff_b,kernel,iterations = 1)
        kernel = np.ones((3,3),np.uint8)  #dilation
        diff_open = cv2.dilate(diff_erosion,kernel,iterations = 1)

        imgName = self._time.strftime('%Y%m%d-%H%M%S-') + 'roi_diff.jpg'
        cv2.imwrite(imgName, diff_open)  #save the eroded/dilated image as difference


        #calculate the no of blobs in difference image
        blobs, num_blobs = ndimage.label(diff_open)
        print 'image name' , self._time.strftime('%Y%m%d-%H%M%S')   

        contours, hierarchy = cv2.findContours(diff_open, cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE) #modifies the image passed as argument
        max  = 0
        count = 0
        area = 0    
        for i in contours:
            area = cv2.contourArea(i)
            if max < area:
                max = area
           
  
        #print 'area', area
    
        if (num_blobs < 30) and ( area > 20):
            verdict = "motion"
        else:
            verdict = "pass"
        return  self._time.strftime('%Y%m%d-%H%M%S'), self._brightness,thresh, num_blobs, max, verdict 
        
