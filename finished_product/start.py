# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import logging.config

st_pin=24
def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(st_pin, GPIO.IN)

def awaiting():
    #ログの設定の読み込み
    logging.config.fileConfig('logging.ini')
    logger = logging.getLogger(__name__)
    while(True):
        value= GPIO.input(st_pin)
        print(value)
        if(value==0):
            logger.info("program start")
            break
        time.sleep(1.0)
    time.sleep(1)#パラシュート展開後待機時間
    return