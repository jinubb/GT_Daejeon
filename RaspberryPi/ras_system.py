#!/usr/bin/env python
## -*- coding: utf-8 -*-  #
 
import cv2


import Seeed_AMG8833
import pygame
import os
import math
import time

import numpy as np
from scipy.interpolate import griddata

from colour import Color

#import serial

def MaskDetect():
    eye_cascade= cv2.CascadeClassifier("./haarcascade_eye.xml")
    nose_cascade = cv2.CascadeClassifier("./haarcascade_mcs_nose.xml")
    cam= cv2.VideoCapture(0)
    stack = 0
    while True:
        ret, frame= cam.read()
        frame = cv2.resize(frame, dsize=(640, 480), interpolation=cv2.INTER_AREA)
        if not ret:
            break
 
        gray= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray)
        if len(eyes)==0:  
            print "not eyes"
        else:  # Detected eyes
            noses = nose_cascade.detectMultiScale(gray)
            if len(noses)==0: #if not nose
                stack=stack+1
                print "not nose!! stack : %d" % stack
                if(stack >= 3):
                    cam.release() 
                    return 0
            else:
                stack = 0
                print "Detected nose, plz wear mask"                


#low range of the sensor (this will be blue on the screen)
MINTEMP = 20

#high range of the sensor (this will be red on the screen)
MAXTEMP = 28

#how many color values we can have
COLORDEPTH = 1024

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()

#initialize the sensor
sensor = Seeed_AMG8833.AMG8833()

points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

#sensor is an 8x8 grid so lets do a square
height = 240
width = 240

#the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30

lcd = pygame.display.set_mode((width, height))

lcd.fill((255,0,0))

pygame.display.update()
pygame.mouse.set_visible(False)

lcd.fill((0,0,0))
pygame.display.update()

#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
    num = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    global mode
    if(num > 1000):
        if(mode == 0):
            mode = 1
            print"high!!"
    return num

#let the sensor initialize
time.sleep(.1)

def Thermal_cam():
    global mode
    cnt = 0
    while (mode == 0 and cnt < 50):

        #read the pixels
        pixels = sensor.read_temp()
        pixels = [map(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
    
        #perdorm interpolation
        bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
    
        #draw everything
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH- 1)], (displayPixelHeight * ix, displayPixelWidth * jx, displayPixelHeight, displayPixelWidth))
    
        pygame.display.update()
        cnt = cnt+1
        print(cnt)


        
#Start message
os.system('mpg321 시스템시작.mp3')
print"시스템 시작"
time.sleep(.1)

while True:
    mode = 0
    '''
    #wait for Ardu
    while True:
        data = arduino.readline().decode("utf-8").strip('\n').strip('\r') # remove newline and carriage return characters
        print("We got: '{}'".format(data))
        if(data == "c"):
            break
    os.system('mpg321 방문자감지.mp3')
    '''

    #열화상감지
    Thermal_cam()

    #Mask Detection
    if(mode == 1):
        os.system('mpg321 마스크착용.mp3')
        print "Start Mask-Detection"
        MaskDetect()
        print "Detected Mask!!"
        time.sleep(1)
    '''
    #손세정
    os.system('mpg321 손넣기.mp3')
    #sand message to Ardu
    arduino = serial.Serial('/dev/ttyACM0',9600)
    pystring = 's'
    pystring = pystring.encode('utf-8')
    arduino.write(pystring)


    #wait for Adu
    while True:
        data = arduino.readline().decode("utf-8").strip('\n').strip('\r') # remove newline and carriage return characters
        print("We got: '{}'".format(data))
        if(data == "a"):
            break
    '''
    
    #Recycle
