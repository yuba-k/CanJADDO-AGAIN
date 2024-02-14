# -*- coding: utf-8 -*-
#逆光回避動作
import cv2  as cv
import numpy as np
from matplotlib import pyplot as plt
import logging
import math
import RPi.GPIO	as GPIO
import time
import datetime
import picamera

#ログの設定
logging.basicConfig(level=logging.INFO)#ログレベルの設定
logger=logging.getLogger('逆光フェーズ')#ログの名前
formatter=logging.Formatter('%(asctime)s:	%(filename)s:	%(lineno)d:	%(levelname)s:	%(message)s')#実行時間
file_handler=logging.FileHandler('/home/pi/sample/history.log',	encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#GPIO初期設定
duty=40
GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
right=GPIO.PWM(27,50)
left=GPIO.PWM(23,50)
right.start(0)
left.start(0)

#グローバル変数
HEIGHT=960
WIDTH=1280
I=0

def	cap():
    global HEIGHT,WIDTH,I
    with picamera.PiCamera() as	camera:
        camera.resolution=(WIDTH,HEIGHT)
        camera.start_preview()
        camera.capture(f'picture{I}.jpg')
        logger.info('Take picture')
    return	0


def backlit():#逆光判定
    global HEIGHT,WIDTH,I
    logger.info('backlight confirmation')
    # 画像を読み込む
    im = cv.imread(f'picture{I}.jpg')
    img=im[HEIGHT//2:HEIGHT,0:WIDTH]#空の情報取得
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)#hsv色範囲変換
    v=hsv[:,:,2]#明度
    # 画像をグレースケールにする。
    gray = cv.cvtColor(hsv, cv.COLOR_BGR2GRAY)
    # 標準偏差を計算する
    _, stddev = cv.meanStdDev(gray)
    print('stddev',stddev)
    logger.info(f'standard deviation:{stddev}')
    if stddev>=15:#逆光でない
        return 0
    else:#逆光
        return -1
    

def avoidance():#逆光回避
    logging.info('Backlight avoidance')
    t_end=time.time()+2
    while time.time()<=t_end:#前進
        right.ChangeDutyCycle(duty)
        right_ph=GPIO.output(22,GPIO.LOW)
        left.ChangeDutyCycle(duty)
        left_ph=GPIO.output(24,GPIO.LOW)
    right.ChangeDutyCycle(0)
    left.ChangeDutyCycle(0)
#    while time.time()+1:#反転(右回り)
#        right.ChangeDutyCycle(0)
#        right_ph=GPIO.output(22,GPIO.LOW)
#        left.ChangeDutyCycle(duty)
#        left_ph=GPIO.output(24,GPIO.LOW)

def main():
    global I
    key=0
    while(True):
        I=I+1
        cap()
        key=backlit()
        if key==-1:
            avoidance()
        else:
            logging.info('FINISH')
            break
                

if	__name__=='__main__':
    main()
