# -*- coding: utf-8 -*-
#ゴール後ブザーを鳴らしゴールを周知する
import RPi.GPIO as GPIO
import time

def buzz():
    GPIO.setmode(BCM)
    GPIO.setup(14,GPIO.OUT)
    t_end=time.time()+20
    while time.time()<=t_end:
        buzzer=GPIO.PWM(14,400)
        buzzer.start(0)
        buzzer.ChangeDutyCycle(50)
    GPIO.cleanup()