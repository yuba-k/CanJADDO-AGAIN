# -*- coding: utf-8 -*-
#ゴール後ブザーを鳴らしゴールを周知する
import RPi.GPIO as GPIO
import time

def buzz():
    buzz=12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzz,GPIO.OUT)

    buzzer=GPIO.PWM(buzz,523)
    buzzer.start(0)
    time.sleep(1)
    buzzer.ChangeDutyCycle(50)

    while True:
        buzzer.ChangeFrequency(523)
        time.sleep(0.02)
        buzzer.ChangeFrequency(658)
        time.sleep(0.02)
        buzzer.ChangeFrequency(784)
        time.sleep(0.02)