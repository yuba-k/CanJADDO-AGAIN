# -*- coding: utf-8 -*-
###
#引数として方向(left,straight,right)、duty比、秒数を与える
###
import logging.config
import RPi.GPIO as GPIO
import time
import datetime


# #ログの設定
# logging.basicConfig(level=logging.INFO)#ログレベルの設定
# logger=logging.getLogger('moter.py')#ログの名前
# formatter=logging.Formatter('%(asctime)s:	%(filename)s:	%(lineno)d:	%(levelname)s:	%(message)s')#実行時間
# file_handler=logging.FileHandler('/home/pi/sample/history.log',	encoding='utf-8')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

def move(direction, duty, sec):
    #ログの設定
#    logging.config.fileConfig('logging.ini')
    logger = logging.getLogger(__name__)
    
    t_end = time.time()
    right_ph = GPIO.output(11, GPIO.LOW)
    left_ph = GPIO.output(19, GPIO.LOW)
    right_duty = left_duty = duty

    logger.info(f"duty:{duty}")
    if direction == "right" or direction=="search":    #右に曲がる
        logger.info("right")
        right_duty *= 0.6       #右足を弱く
#	      left_duty = duty
        
    elif direction == "left":   #左に曲がる
        logger.info("left")
#       right_duty = duty
        left_duty *= 0.6        #左足を弱く
        
    elif direction == "straight" or direction=="goal":   #まっすぐ
        logger.info(f"straight")
#       right_duty = duty
#	      left_duty = duty
    elif direction=="back":
        logger.info(f"back")
        right_ph = GPIO.output(r_ph, GPIO.HIGH) #モーターを反転
        left_ph = GPIO.output(l_ph, GPIO.HIGH)
#       right_duty = duty
#	    left_duty = duty
        
    left_duty += 1
    while time.time() <= t_end + sec:   #実際に動く
        right.ChangeDutyCycle(right_duty)
        left.ChangeDutyCycle(left_duty)
        
    right.ChangeDutyCycle(0)
    left.ChangeDutyCycle(0)
    time.sleep(2)   #モータードライバのオーバーヒート対策

def advance(direction, duty, sec):
    move(direction,duty,sec)

def search(duty,sec_1):
    move("right",duty,sec_1)


def avoidance(duty,sec_1,sec_2):#逆光回避
    move("straight",duty,sec_1)
    move("right",duty,sec_2)

def para(duty,sec_1,sec_2):
    move("back",duty,sec_1)
    move("right",duty,3)
    move("straight",duty,sec_2)

def init():
    global r_ph,l_ph,r_pwm,l_pwm,right,left
    right=None
    left=None
    GPIO.setwarnings(False)
    r_ph=11
    l_ph=19
    r_pwm=13
    l_pwm=26
    #GPIO初期設定
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(r_pwm,GPIO.OUT)
    GPIO.setup(r_ph,GPIO.OUT)
    GPIO.setup(l_pwm,GPIO.OUT)
    GPIO.setup(l_ph,GPIO.OUT)
    right = GPIO.PWM(r_pwm, 200)    #PWMの周波数は必ず100以上！！ 100未満にすると1パルスにおけるタイヤを動かす負荷が大きく，
    left = GPIO.PWM(l_pwm, 200)     #モータードライバが担う電流量や電力量が過度に増加．波形や動きが不安定に！！
    right.start(0)
    left.start(0)