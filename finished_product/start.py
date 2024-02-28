# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN)

def awaiting():
    while(True):
        value= GPIO.input(16)
        print(value)
        if(value==0):
            break
        time.sleep(1.0)
    time.sleep(30)#パラシュート展開後待機時間
GPIO.cleanup()