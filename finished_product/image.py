# -*- coding: utf-8 -*-
#物体検出からモータ動作のみ
import cv2  as cv
import numpy as np
#from matplotlib import pyplot as plt
#from PIL import Image
import logging.config
import math
#import RPi.GPIO	as GPIO
import camera
import motor
#import time
#import datetime
#import picamera

# #ログの設定
# logging.basicConfig(level=logging.INFO)#ログレベルの設定
# logger=logging.getLogger('画像処理フェーズ')#ログの名前
# formatter=logging.Formatter('%(asctime)s:	%(filename)s:	%(lineno)d:	%(levelname)s:	%(message)s')#実行時間
# file_handler=logging.FileHandler('/home/pi/sample/history.log',	encoding='utf-8')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

def detection():
    if not hasattr(detection, 'count'):
        detection.count = 0
#    logging.config.fileConfig('logging.ini')
    logger = logging.getLogger(__name__)
    logger.info("color cone detection")
    #画像読み込み
    camera.cap(960,1280, f'ImageDetect-{detection.count}.jpg')
    img=cv.imread(f'ImageDetect-{detection.count}.jpg')
    detection.count += 1
    img=cv.flip(img,-1)
    HEIGHT,WIDTH,_=img.shape#画像サイズ取得
    # 赤色の検出
    # HSV色空間に変換
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    # # 赤色のHSVの値域1
    # hsv_min = np.array([0,64,0])
    # hsv_max = np.array([2,255,255])
    # mask1 = cv.inRange(hsv, hsv_min, hsv_max)
    # 赤色のHSVの値域2
    hsv_min = np.array([165,130,100])
    hsv_max = np.array([179,255,255])
    mask2 = cv.inRange(hsv, hsv_min, hsv_max)
    # 赤色領域のマスク（255：赤色、0：赤色以外）
    # mask = mask1 + mask2
    mask=mask2
    # マスキング処理
    masked_img = cv.bitwise_and(img, img, mask=mask)
    cv.imwrite(f"masked.jpg",masked_img)
    # 画像を読み込む
    gray = cv.imread(f"masked.jpg", cv.IMREAD_GRAYSCALE)#二値化込み
    ret,th_img = cv.threshold(gray,0,255,cv.THRESH_OTSU)# 入力画像（グレースケール画像を指定すること）# 閾値 # 閾値を超えた画素に割り当てる値# 閾値処理方法
    # 膨張・収縮処理#オープニング処理
    # 近傍の定義
    neiborhood = np.array([[0, 1, 0],[1, 1, 1],[0, 1, 0]],np.uint8)
    # 収縮
    img_erode = cv.erode(th_img,neiborhood,iterations=1)
    # 膨張
    img_dilate = cv.dilate(img_erode,neiborhood,iterations=1)
    cv.imwrite(f'dilate.jpg',img_dilate)
    # 輪郭抽出
    # OpenCV 3 の場合
    contours,hierarchy= cv.findContours(img_dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_TC89_KCOS)
    # 小さい輪郭は誤検出として削除する
    contours = list(filter(lambda x: cv.contourArea(x) > 200, contours))
    # 一番面積が大きい輪郭を選択する。
    if not contours or all(cv.contourArea(x) == 0 for x in contours):
        logger.info("no red")
        return "search"
    else:
        print("not empty")
        max_cnt = max(contours, key=lambda x: cv.contourArea(x))
    # 黒い画像に一番大きい輪郭だけ塗りつぶして描画する
    out = np.zeros_like(gray)
    cv.drawContours(out, [max_cnt], -1, color=255, thickness=-1)
    cv.imwrite(f'dilate.jpg', out)
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
        out=cv.imread(f'dilate.jpg')
        if y_t==0:
            moter.advance("right",70,0.3)
        if bottom>=1000:#要調整
            return "goal"
        else:
            if x_center<=(WIDTH//3):
                motor.advance("left",70,0.5)
            elif (WIDTH//3)<x_center and x_center<(WIDTH//3*2):
                motor.advance("straight",70,2.0)
            else:
                motor.advance("right",70,0.5)
        return
    else:
        logger.info('no tri')
        return "search"
