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
#python-library
import time
import logging

#ログの設定の読み込み
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

#強制終了の設定
beginning=time.time()#競技開始時間
close=beginning+(18*60)#強制終了時間

#main
start.awaiting()#着地展開まで待機
direction="default"
while direction!=0:#パラシュート回避
    camera.cap(320,240)
    direction=pa.parachute()
    motor.move(direction,20,1.0)
gps.main()#位置情報による接近
t_end=time.time()+60
while True:#逆光回避
    if time.time()>=t_end and direction=="search":
        gps.main()
        t_end=time.time()+60
    camera.cap(320,240)
    key=backlib.backlight()
    if key==-1:
        motor.avoidance(20,4.0,1.5)#duty比/直進時間[s]/右折時間[s]
    else:
        pass
    camera.cap(960,1280)
    direction=image.detection()
    motor.move(direction,20,1.0)
    if direction=="goal":
        logging.info("goal!!")
        break
    else:
        pass
    if time.time()>=close:
        logging.info("Forced termination/goal judgment")

logger.info("End of all phases")