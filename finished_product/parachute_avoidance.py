# -*- coding: utf-8 -*-
import cv2  as cv
import math
import numpy as np
import picamera
import logging.config
import RPi.GPIO	as GPIO
import time
from PIL import image

#ログの設定の読み込み
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

#グローバル変数
r_ph=22
l_ph=24
r_pwm=27
l_pwm=23
#GPIO初期設定
duty=60
GPIO.setmode(GPIO.BCM)
GPIO.setup(r_pwm,GPIO.OUT)
GPIO.setup(r_ph,GPIO.OUT)
GPIO.setup(l_pwm,GPIO.OUT)
GPIO.setup(l_ph,GPIO.OUT)
right=GPIO.PWM(r_pwm,200)
left=GPIO.PWM(l_pwm,200)
right.start(0)
left.start(0)

def parachute():
    img=cv.imread(f"picture.jpg")
    HEIGHT,WIDTH=img.size
    img=cv.flip(img,-1)
    img=img[HEIGHT//2:HEIGHT,0:WIDTH]#空の情報取得
    #二値化
    dst = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imwrite(f"gray.jpg",dst)
    _,img_th=cv.threshold(dst,100,255,cv.THRESH_BINARY)
    cv.imwrite(f"binary.jpg",img_th)
    img=cv.imread(f"binary.jpg",cv.IMREAD_GRAYSCALE)
    #黒部分の画素数
    all_area=HEIGHT//2*WIDTH
    white_area=cv.countNonZero(img)
    black_area=all_area-white_area
    if black_area>=0.2:
        direction="back"
        logging.info("Parachute avoidance behavior")
    else:
        direction=0
        logging.info("not recognizing the parachute")
    return direction