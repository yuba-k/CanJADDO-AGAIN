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
r_ph=13
l_ph=26
r_pwm=9
l_pwm=19
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
GPIO.setup(r_pwm,GPIO.OUT)
GPIO.setup(r_ph,GPIO.OUT)
GPIO.setup(l_pwm,GPIO.OUT)
GPIO.setup(l_ph,GPIO.OUT)
right=GPIO.PWM(r_pwm,200)
left=GPIO.PWM(l_pwm,200)
right.start(0)
left.start(0)


def	cap():
    global HEIGHT,WIDTH,I
    with picamera.PiCamera() as	camera:
        camera.exposure_mode = 'off' #露出モード 
        camera.meter_mode = 'average' #測光モード
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
        if bottom>=1000:#要調整
            return 1
        return x_center
    else:
       logger.info('no tri')
       return -1
   
   
def moter(direction):
    global WIDTH,r_ph,l_ph
    logger.info('motor control')
    t_end=time.time()+1.0
    if coordinate<=(WIDTH//3):
        while time.time()<=t_end:
            right.ChangeDutyCycle(duty)
            right_ph=GPIO.output(r_ph,GPIO.LOW)
            left.ChangeDutyCycle(0)
            left_ph=GPIO.output(l_ph,GPIO.HIGH)
        logging.info('left fin')
    if (WIDTH//3)<coordinate and coordinate<(WIDTH//3*2):
        while time.time()<=t_end:
            right.ChangeDutyCycle(duty)
            right_ph=GPIO.output(r_ph,GPIO.LOW)
            left.ChangeDutyCycle(duty)
            left_ph=GPIO.output(l_ph,GPIO.LOW)
        logging.info('forward fin')
    if (WIDTH//3*2)<=coordinate and coordinate<=WIDTH:
        while time.time()<=t_end:
            right.ChangeDutyCycle(0)
            right_ph=GPIO.output(r_ph,GPIO.HIGH)
            left.ChangeDutyCycle(duty)
            left_ph=GPIO.output(l_ph,GPIO.LOW)
        logging.info('right fin')
#    right.ChangeDutyCycle(0)
#    left.ChangeDutyCycle(0)
   
def goal():
    logger.info('Just before the goal!')
    t_end=time.time()+3
    while time.time()<=t_end:
        right.ChangeDutyCycle(duty)
        right_ph=GPIO.output(22,GPIO.LOW)
        left.ChangeDutyCycle(duty)
        left_ph=GPIO.output(24,GPIO.LOW)
    logger.info('GOAL!!')

def search():
    global r_ph,l_ph
    logger.info("serch")
    t_end=time.time()+1.0
    while time.time()<=t_end:
        right.ChangeDutyCycle(0)
        right_ph=GPIO.output(r_ph,GPIO.HIGH)
        left.ChangeDutyCycle(duty)
        left_ph=GPIO.output(l_ph,GPIO.LOW)

def main():
    global I
    key=0
    while(True):
        cap()
        key=detection()
        if key==-1:
            search()
        elif key==1:
            goal()
            break
        else:
            moter(key)
        I=I+1
        

if	__name__=='__main__':
    main()