# -*- coding: utf-8 -*-

import cv2  as cv
import math
import numpy as np

def parachute(HEIGHT,WIDTH):
    img=cv.imread("picture.jpg")
    hsv=cv.cvtColor(img,cv.COLOR_BGR2HSV)#BGR to HSV
    #色検出閾値の設定
    lower=np.array([90,64,0])#色相値(Hue値)/彩度/明度
    upper=np.array([150,255,255])
    #色検出閾値範囲内の色を抽出するマスクを作成
    frame_mask=cv.inRange(hsv,lower,upper)
    #論理演算で色検出
    dst=cv.bitwise_and(img,img,mask=frame_mask)
    cv.imwrite("color.jpg",dst)
    #二値化
    #_,img_th=cv.threshold(dst,0,255,cv.THRESH_BINARY)
    #cv.imwrite("binary.jpg",img_th)
    img_gray= cv.cvtColor(dst,cv.COLOR_BGR2GRAY)
    clp1=img_gray[0:HEIGHT,0:WIDTH//3]
    clp2=img_gray[0:HEIGHT,WIDTH//3:WIDTH//3*2]
    clp3=img_gray[0:HEIGHT,WIDTH//3*2:WIDTH]
    #白部分の画素数
    white_area_1=cv.countNonZero(clp1)
    white_area_2=cv.countNonZero(clp2)
    white_area_3=cv.countNonZero(clp3)
    max_area=max(white_area_1,white_area_2,white_area_3)
#    if max_area<______ #面積が_____以下ならパラシュートなしとみなす
#        return 0
    if max_area==white_area_1:
        print("right")
        return "right"
    elif max_area==white_area_2:
        print("back")
        return "back"
    else:
        print("left")
        return "left"