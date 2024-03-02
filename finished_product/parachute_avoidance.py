# -*- coding: utf-8 -*-
import cv2  as cv
#import math
#import numpy as np
import camera
import motor
import logging.config
#import time
#from PIL import Image

#ログの設定の読み込み
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)


def parachute():
    camera.cap(240,320)
    img=cv.imread(f"picture.jpg")
    HEIGHT, WIDTH, _=img.shape
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
        motor.para()
        logging.info("Parachute avoidance behavior")
    else:
        logging.info("not recognizing the parachute")
    return