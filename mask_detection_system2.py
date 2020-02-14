#!/usr/bin/env python
## -*- coding: utf-8 -*-  #
 
import cv2
import time
import RPi.GPIO as GPIO
import os
import time
import pygame
 


def HelloPerson():
    
    #핀 넘버링을 BCM 방식을 사용한다.
    GPIO.setmode(GPIO.BCM)

    GPIO.setwarnings(False)
 
    # HC-SR04의 트리거 핀을 GPIO 17번, 에코핀을 GPIO 27번에 연결한다.
    GPIO_TRIGGER = 2 
    GPIO_ECHO = 3

    # 초음파를 내보낼 트리거 핀은 출력 모드로, 반사파를 수신할 에코 피은 입력 모드로 설정한다.
    GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
    GPIO.setup(GPIO_ECHO,GPIO.IN)

    try:
        while True : # if not coming
            stop = 0
            start = 0
            # 먼저 트리거 핀을 OFF 상태로 유지한다
            GPIO.output(GPIO_TRIGGER, False)
            time.sleep(2)
 
            # 10us 펄스를 내보낸다. 
            # 파이썬에서 이 펄스는 실제 100us 근처가 될 것이다.
            # 하지만 HC-SR04 센서는 이 오차를 받아준다.
            GPIO.output(GPIO_TRIGGER, True)
            time.sleep(0.00001)
            GPIO.output(GPIO_TRIGGER, False)
 
            # 에코 핀이 ON되는 시점을 시작 시간으로 잡는다.
            while GPIO.input(GPIO_ECHO)==0:
                start = time.time()
 
            # 에코 핀이 다시 OFF되는 시점을 반사파 수신 시간으로 잡는다.
            while GPIO.input(GPIO_ECHO)==1:
                stop = time.time()
 
            # Calculate pulse length
            elapsed = stop-start
 
            # 초음파는 반사파이기 때문에 실제 이동 거리는 2배이다. 따라서 2로 나눈다.
            # 음속은 편의상 340m/s로 계산한다. 현재 온도를 반영해서 보정할 수 있다.
            if (stop and start):
                distance = (elapsed * 34000.0) / 2
                if distance <= 100: # coming person
                    print "1m 이내 방문자 감지"
                    print "거리 : %.1f cm" % distance
                    return 0
                else:
                    print"방문자 없음"
                
    except KeyboardInterrupt:   
        print "End"
        GPIO.cleanup()


def MaskDetect():
    eye_cascade= cv2.CascadeClassifier("./haarcascade_eye.xml")
    nose_cascade = cv2.CascadeClassifier("./haarcascade_mcs_nose.xml")
    cam= cv2.VideoCapture(0)
    stack = 0
    while True:
        
        ret, frame= cam.read()
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
                    print "Detected Mask!!"
                    cam.release() 
                    #cv2.destroyAllWindows()
                    return 0
            else:
                stack = 0
                print "Detected nose, plz wear mask"                
 

#Start message
pygame.init()
sound = pygame.mixer.Sound('start.wav')
sound.play()
print"start system"
time.sleep(1)

#Body
HelloPerson()

os.system('omxplayer coming.mp3')  # message to coming person
time.sleep(2)
                  
print "Start Mask-Detection"
MaskDetect()

os.system('omxplayer hand.mp3')
time.sleep(2)
                  
#sand message to Adu

#wait for Adu
#Recycle


