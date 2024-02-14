# -*- coding: utf-8 -*-
#物体検出からモータ動作のみ
import cv2  as cv
import numpy as np
from matplotlib import pyplot as plt
import logging
import math
import RPi.GPIO	as GPIO
import time
import datetime
import picamera

#グローバル変数
HEIGHT=960#画像ピクセル数(縦)
WIDTH=1280#画像ピクセル数(横)
I=0


#ログの設定
logging.basicConfig(level=logging.INFO)#ログレベルの設定
logger=logging.getLogger('画像処理フェーズ')#ログの名前
formatter=logging.Formatter('%(asctime)s:	%(filename)s:	%(lineno)d:	%(levelname)s:	%(message)s')#実行時間
file_handler=logging.FileHandler('/home/pi/sample/history.log',	encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#GPIO初期設定
duty=30
GPIO.setmode(GPIO.BCM)
GPIO.setup(6,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)
right=GPIO.PWM(6,50)
left=GPIO.PWM(19,50)
right.start(0)
left.start(0)


def	cap():
    global HEIGHT,WIDTH,I
    with picamera.PiCamera() as	camera:
        camera.resolution=(WIDTH,HEIGHT)
        camera.start_preview()
        camera.capture(f'picture{I}.jpg')
        logger.info('Take picture')
    right.ChangeDutyCycle(0)
    left.ChangeDutyCycle(0)
    return	0


def detection():
    global HEIGHT,WIDTH,I
    logger.info("color cone detection")
    #画像読み込み
    img=cv.imread(f"picture{I}.jpg")
    img=cv.flip(img,-1)
    # 赤色の検出
    # HSV色空間に変換
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    # 赤色のHSVの値域1
    hsv_min = np.array([0,64,0])
    hsv_max = np.array([2,255,255])
    mask1 = cv.inRange(hsv, hsv_min, hsv_max)
    # 赤色のHSVの値域2
    hsv_min = np.array([165,64,0])
    hsv_max = np.array([179,255,255])
    mask2 = cv.inRange(hsv, hsv_min, hsv_max)
    # 赤色領域のマスク（255：赤色、0：赤色以外）
    mask = mask1 + mask2
    # マスキング処理
    masked_img = cv.bitwise_and(img, img, mask=mask)
    cv.imwrite(f"masked{I}.jpg",masked_img)
    # 画像を読み込む
    gray = cv.imread(f"masked{I}.jpg", cv.IMREAD_GRAYSCALE)#二値化込み
    ret,th_img = cv.threshold(gray,0,255,cv.THRESH_OTSU)# 入力画像（グレースケール画像を指定すること）# 閾値 # 閾値を超えた画素に割り当てる値# 閾値処理方法
    # 膨張・収縮処理#オープニング処理
    # 近傍の定義
    neiborhood = np.array([[0, 1, 0],[1, 1, 1],[0, 1, 0]],np.uint8)
    # 収縮
    img_erode = cv.erode(th_img,neiborhood,iterations=1)
    # 膨張
    img_dilate = cv.dilate(img_erode,neiborhood,iterations=1)
    cv.imwrite(f'dilate{I}.jpg',img_dilate)
    # 輪郭抽出
    # OpenCV 3 の場合
    contours,hierarchy= cv.findContours(img_dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_TC89_KCOS)
    # 小さい輪郭は誤検出として削除する
    contours = list(filter(lambda x: cv.contourArea(x) > 800, contours))
    # 一番面積が大きい輪郭を選択する。
    if not contours or all(cv.contourArea(x) == 0 for x in contours):
        logger.info("no red\n")
        return -1
    else:
        print("not empty")
        max_cnt = max(contours, key=lambda x: cv.contourArea(x))
    # 黒い画像に一番大きい輪郭だけ塗りつぶして描画する
    out = np.zeros_like(gray)
    cv.drawContours(out, [max_cnt], -1, color=255, thickness=-1)
    cv.imwrite(f'dilate{I}.jpg', out)
    h,w=out.shape[:2]
    # 白い部分の座標を取得する#幅:高=3:7
    white_pixels = np.where(out == 255)
    x_t, y_t = white_pixels[1][0], white_pixels[0][0]
    logger.info(f' top |x:{x_t},y:{y_t}')
    out=cv.rotate(out,cv.ROTATE_90_CLOCKWISE)#時計回りに90度
    white_pixels = np.where(out == 255)
    y_l, x_l = HEIGHT-(white_pixels[1][0]), white_pixels[0][0]
    logger.info(f' left|x:{x_l},y:{y_l}')
    out=cv.rotate(out,cv.ROTATE_90_COUNTERCLOCKWISE)
    out=cv.rotate(out,cv.ROTATE_90_COUNTERCLOCKWISE)#半時計回りに90度
    white_pixels = np.where(out == 255)
    y_r, x_r = white_pixels[1][0], WIDTH-(white_pixels[0][0])
    logger.info(f'right|x:{x_r},y:{y_r}')
    bottom=x_r-x_l#底辺
    length=y_t-((y_l+y_r)//2)#高さ
    x_center=(x_l+x_r)//2#底辺中心座標
    if (math.isclose(bottom/length,1/2, rel_tol=0, abs_tol=100.0))==True:
        logger.info("tri")
        out=cv.imread(f'dilate{I}.jpg')
#        cv.line(out,
#            pt1=(x_l, y_l),
#            pt2=(x_t, y_t),
#            color=(0, 0, 255),
#            thickness=3,
#            lineType=cv.LINE_4,
#            shift=0)
#        cv.imwrite(f'tri{I}.jpg', out)
#        out=cv.imread(f'tri{I}.jpg')
#        cv.line(out,
#                 pt1=(x_t, y_t),
#                 pt2=(x_r, y_r),
#                 color=(0, 255, 0),
#                 thickness=3,
#                 lineType=cv.LINE_4,
#                 shift=0)
#        cv.imwrite(f'tri{I}.jpg', out)
#        out=cv.imread(f'tri{I}.jpg')
#        cv.line(out,
#                 pt1=(x_l, y_l),
#                 pt2=(x_r, y_r),
#                 color=(255, 0, 0),
#                 thickness=3,
#                 lineType=cv.LINE_4,
#                 shift=0)
#        cv.imwrite(f'tri{I}.jpg', out)
        if bottom>=1000:#要調整
            return 1
        return x_center
    else:
       logger.info('no tri')
       return -1
   
   
def moter(coordinate):
    global WIDTH
    logger.info('motor control')
    t_end=time.time()+1.0
    if coordinate<=(WIDTH//3):
        while time.time()<=t_end:
            right.ChangeDutyCycle(duty)
            right_ph=GPIO.output(13,GPIO.LOW)
            left.ChangeDutyCycle(0)
            left_ph=GPIO.output(26,GPIO.HIGH)
        logging.info('left fin')
    if (WIDTH//3)<coordinate and coordinate<(WIDTH//3*2):
        while time.time()<=t_end:
            right.ChangeDutyCycle(duty)
            right_ph=GPIO.output(13,GPIO.LOW)
            left.ChangeDutyCycle(duty)
            left_ph=GPIO.output(26,GPIO.LOW)
        logging.info('forward fin')
    if (WIDTH//3*2)<=coordinate and coordinate<=WIDTH:
        while time.time()<=t_end:
            right.ChangeDutyCycle(0)
            right_ph=GPIO.output(13,GPIO.HIGH)
            left.ChangeDutyCycle(duty)
            left_ph=GPIO.output(26,GPIO.LOW)
        logging.info('right fin')
#    right.ChangeDutyCycle(0)
#    left.ChangeDutyCycle(0)
   
def goal():
#    logger.info('Just before the goal!')
#    t_end=time.time()+3
#    while time.time()<=t_end:
#        right.ChangeDutyCycle(duty)
#        right_ph=GPIO.output(22,GPIO.LOW)
#        left.ChangeDutyCycle(duty)
#        left_ph=GPIO.output(24,GPIO.LOW)
    logger.info('GOAL!!')

def main():
    global I
    key=0
    while(True):
        cap()
        key=detection()
        if key==-1:
            pass
        elif key==1:
            goal()
            break
        else:
            moter(key)
        I=I+1
        

if	__name__=='__main__':
    main()