# -*- coding: utf-8 -*-
import cv2  as cv
#import math
#import numpy as np
import camera
import motor
import logging.config
import RPi.GPIO	as GPIO
import time
from PIL import Image 

def parachute():
    #ログの設定の読み込み
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger(__name__)
    
    img=cv.imread(f"picture.jpg")
    img=cv.flip(img,-1)
    HEIGHT,WIDTH,_=img.shape

    #二値化
    dst = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imwrite(f"gray.jpg",dst)
    _,img_th=cv.threshold(dst,50,255,cv.THRESH_BINARY)
    cv.imwrite(f"binary.jpg",img_th)
    img=cv.imread(f"binary.jpg",cv.IMREAD_GRAYSCALE)
    #黒部分の画素数
    all_area=HEIGHT*WIDTH
    white_area=cv.countNonZero(img)
    black_area=all_area-white_area
    
    values=black_area/all_area*100
    if values>=2:#黒が%以上ならパラシュートアリと判断
        motor.para(50,10,10)
    logger.info(f"{values}%")
    return
