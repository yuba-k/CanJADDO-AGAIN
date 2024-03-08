# -*- coding: utf-8 -*-
#逆光回避動作
import cv2  as cv
#import numpy as np
#from matplotlib import pyplot as plt
import logging.config
import camera
import motor
#import math
#import RPi.GPIO	as GPIO
#import time
#import datetime

# #ログの設定
# logging.basicConfig(level=logging.INFO)#ログレベルの設定
# logger=logging.getLogger('backlib')#ログの名前
# formatter=logging.Formatter('%(asctime)s:	%(filename)s:	%(lineno)d:	%(levelname)s:	%(message)s')#実行時間
# file_handler=logging.FileHandler('/home/pi/sample/history.log',	encoding='utf-8')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)


def backlight():#逆光判定   return:is backlight
    #ログの設定
#    logging.config.fileConfig('logging.ini')
    logger = logging.getLogger(__name__)
    
    logger.info('backlight confirmation')
    # 画像を読み込む
    camera.cap(240,320, 'backlit.jpg')
    im = cv.imread(f'backlit.jpg')
    HEIGHT,WIDTH,_=im.shape
    # img=im[HEIGHT//2:HEIGHT,0:WIDTH]#空の情報取得
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)#hsv色範囲変換
    v=hsv[:,:,2]#明度
    # 画像をグレースケールにする。
    gray = cv.cvtColor(hsv, cv.COLOR_BGR2GRAY)
    # 標準偏差を計算する
    _, stddev = cv.meanStdDev(gray)
    logger.info(f'standard deviation:{stddev}')
    if stddev<5:#逆光なら
        motor.avoidance(50,15,2.0)#duty比/直進時間[s]/右折時間[s]
        return True
    return False
