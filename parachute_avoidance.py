# -*- coding: utf-8 -*-

import cv2  as cv
import math
import numpy as np
import time
#import picamera

#GPIO初期設定
# duty=30
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(r_pwm,GPIO.OUT)
# GPIO.setup(r_ph,GPIO.OUT)
# GPIO.setup(l_pwm,GPIO.OUT)
# GPIO.setup(l_ph,GPIO.OUT)
# right=GPIO.PWM(r_pwm,200)
# left=GPIO.PWM(l_pwm,200)
# right.start(0)
# left.start(0)

WIDTH=320
HEIGHT=240

# with picamera.PiCamera() as	camera:
#     camera.exposure_mode = 'off' #露出モード 
#     camera.meter_mode = 'average' #測光モード
#     camera.resolution=(WIDTH,HEIGHT)
#     camera.start_preview()
#     camera.capture(f'picture.jpg')
#     logger.info('Take picture')
# right.ChangeDutyCycle(0)
# left.ChangeDutyCycle(0)

img=cv.imread("picture.jpg")
hsv=cv.cvtColor(img,cv.COLOR_BGR2HSV)#色検出閾値の設定
lower=np.array([90,64,0])#色相値(Hue値)/彩度/明度
upper=np.array([150,255,255])
#色検出閾値範囲内の色を抽出するマスクを作成
frame_mask=cv.inRange(hsv,lower,upper)
#論理演算で色検出
dst=cv.bitwise_and(img,img,mask=frame_mask)
cv.imwrite("color.jpg",dst)
#特定の範囲のGaussian分布から閾値を自動で決めて二値化
_,img_th=cv.threshold(dst,0,255,cv.THRESH_BINARY)
cv.imwrite("binary.jpg",img_th)
img=cv.imread("binary.jpg",cv.IMREAD_GRAYSCALE)
clp1=img[0:HEIGHT,0:WIDTH//3]
clp2=img[0:HEIGHT,WIDTH//3:WIDTH//3*2]
clp3=img[0:HEIGHT,WIDTH//3*2:WIDTH]

#全体の画素数
whole_area=clp1.size
#白部分の画素数
white_area_1=cv.countNonZero(clp1)
white_area_2=cv.countNonZero(clp2)
white_area_3=cv.countNonZero(clp3)
max_area=max(white_area_1,white_area_2,white_area_3)
if max_area==white_area_1:
    direction="right"
elif max_area==white_area_2:
    direction="stright"
else:
    direction="left"

print(f"{direction}")

t_end=time.time()+1.0