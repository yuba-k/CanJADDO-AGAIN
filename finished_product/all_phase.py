# -*- coding: utf-8 -*-
#python-code
import logging.config
import camera
import motor
import start
import gps
import parachute_avoidance as pa
import backlib
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
cnt=0

#main
try:
    motor.init()
    start.awaiting()#着地展開まで待機
    direction="default"
    while direction!=0:#パラシュート回避
        camera.cap(320,240)
        direction=pa.parachute()
        if direction==-1:
            motor.pra(40,10,10)#後進時間,右転後の前進時間
    gps.main()#位置情報による接近
    t_end=time.time()+60
    while True:
        if time.time()>=t_end and cnt==60:
            gps.main()
            t_end=time.time()+30
        camera.cap(320,240)
        key=backlib.backlight()
        if key==-1:
            motor.avoidance(20,30,2.0)#duty比/直進時間[s]/右折時間[s]
        camera.cap(960,1280)
        direction=image.detection()
        if direction=="search":
            motor.search(50,1.0)
            cnt=cnt+1
            if cnt==8:
                while key!=-1:
                    key=backlib.backlight()
                    motor.avoidance(20,30,2.0)
                cnt=0
            else:
                pass
        motor.advance(direction,20,1.0)
        if direction=="goal":
            logging.info("goal!!")
            bz.buzz()
            break
        else:
            pass
        if time.time()>=close:
            bz.buzz()
            logging.info("Forced termination/goal judgment")

    logger.info("End of all phases")
    GPIO.cleanup()

except KeyboardInterrupt:
    print("****************end********************")
    GPIO.cleanup()