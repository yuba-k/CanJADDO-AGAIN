# -*- coding: utf-8 -*-
#python-code
import logging.config
import camera
import motor
import start
import gps
import parachute_avoidance as pa
import backlit
import image
import buzzer as bz
#python-library
import time
import logging
import RPi.GPIO as GPIO

#ログの設定の読み込み
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

#強制終了の設定
beginning=time.time()#競技開始時間
close=beginning+(19*60)#強制終了時間

#カウント
detect_counter = 0
backlit_counter = 0
timer = 0

#初期化
motor.init()
start.init()
gps.init()
bz.init()

#main
try:
    scene = "waiting start"
    
    start.awaiting()#着地展開まで待機
    scene = "start"
    
    pa.parachute()
    scene = "search_with_GPS"

    while True:
        if scene == "search_with_GPS":  #位置情報による接近
            gps.main()
            scene = "first_avoid_backlit"
            
        if scene == "first_avoid_backlit":    #逆光回避（初回）
            IsBacklit = backlit.backlight()                
        
        if scene == "detect_with_camera":   #カメラによるコーン検知
            image.detection()
            detect_counter+=1
            if detect_counter >= 10:
                scene = "avoid_backlit"
        
        if scene == "avoid_backlit":
            IsBacklit = backlit.backlight()
            if IsBacklit:
                backlit_counter+=1
            else:
                scene = "search_with_GPS"
            if backlit_counter >= 4:
                scene = "search_with_GPS"
            
        if scene=="goal":
            logging.info("goal!!")
            bz.buzz()
            break
        
        if time.time()>=close:
            bz.buzz()
            logging.info("Forced termination/goal judgment")
            
    logger.info("End of all phases")
    GPIO.cleanup()

except KeyboardInterrupt:
    print("****************end********************")
    GPIO.cleanup()