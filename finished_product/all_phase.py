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
import picamera

#ログの設定の読み込み
logging.config.fileConfig('/home/pi/yuba/sample/finished_product/logging.ini')
logger = logging.getLogger(__name__)

#強制終了の設定
beginning=time.time()#競技開始時間
close=beginning+(18*60)#強制終了時間

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
    

#    pa.parachute()
    scene = "search_with_GPS"

    while True:
        if scene == "search_with_GPS":  #位置情報による接近
            gps.main()
            detect_counter = 0
            scene = "first_avoid_backlit"
            
        if scene == "first_avoid_backlit":    #逆光回避（初回）
            IsBacklit = backlit.backlight()
            detect_counter = 0
            backlit_counter = 0
        scene = "detect_with_camera"               
        
        if scene == "detect_with_camera":   #カメラによるコーン検知
            backlit_counter = 0
            result = image.detection()
            if result == 'search':
                motor.search(70, 0.5)
                detect_counter+=1
            elif result == 'goal':
                scene = 'goal'
            
            if detect_counter >= 25:
                scene = "avoid_backlit"
        
        if scene == "avoid_backlit":
            detect_counter = 0
            IsBacklit = backlit.backlight()
            if IsBacklit:
                backlit_counter += 1
            else:
                scene = "search_with_GPS"
            if backlit_counter >= 4:
                scene = "search_with_GPS"
            
        if scene=="goal":
            motor.advance("goal", 50, 3)
            logging.info("goal!!")
            bz.buzz()
            break
        
        if time.time()>=close:
            bz.buzz()
            logger.info("Forced termination/goal judgment")
            break
            
    logger.info("End of all phases")
    GPIO.cleanup()

except KeyboardInterrupt:
    print("****************end********************")
    GPIO.cleanup()

except picamera.exc.PiCameraError:
    logger.info("camera did not work")
    motor.advance("goal", 40, 3)
    logging.info("goal!!")
    bz.buzz()
    GPIO.cleanup
