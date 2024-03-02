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
    global r_ph,l_ph,r_pwm,l_pwm,right,left
    GPIO.setmode(GPIO.BCM)
    logging.config.fileConfig('logging.ini')
    logger = logging.getLogger(__name__)
    t_end = time.time()
    right_ph = GPIO.output(r_ph, GPIO.LOW)
    left_ph = GPIO.output(l_ph, GPIO.LOW)

    if direction == "right" or direction=="search":
        logger.info(f"duty:{duty}")
        logger.info(f"right")
        while time.time() <= t_end + sec:
            right.ChangeDutyCycle(duty*0.5)
            left.ChangeDutyCycle(duty)
        right.ChangeDutyCycle(0)
        left.ChangeDutyCycle(0)
    elif direction == "left":
        logger.info(f"duty:{duty}")
        logger.info(f"left")
        while time.time() <= t_end + sec:
            right.ChangeDutyCycle(duty)
            left.ChangeDutyCycle(duty*0.5)
        right.ChangeDutyCycle(0)
        left.ChangeDutyCycle(0)
    elif direction == "straight" or direction=="goal":
        logger.info(f"duty:{duty}")
        logger.info(f"straight")
        while time.time() <= t_end + sec:
            right.ChangeDutyCycle(duty)
            left.ChangeDutyCycle(duty)
        right.ChangeDutyCycle(0)
        left.ChangeDutyCycle(0)
    elif direction=="back":
        right_ph = GPIO.output(r_ph, GPIO.HIGH)
        left_ph = GPIO.output(l_ph, GPIO.HIGH)
        logger.info(f"duty:{duty}")
        logger.info(f"back")
        while time.time() <= t_end + sec:
            right.ChangeDutyCycle(duty)
            left.ChangeDutyCycle(duty)
        right.ChangeDutyCycle(0)
        left.ChangeDutyCycle(0)
    return

def advance(direction, duty, sec):
    move(direction,duty,sec)

def search(duty,sec_1):
    move("right",duty,sec_1)


def avoidance(duty,sec_1,sec_2):#逆光回避
    move("straight",duty,sec_1)
    move("right",duty,sec_2)

def pra(duty,sec_1,sec_2):
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
    right=GPIO.PWM(r_pwm,200)
    left=GPIO.PWM(l_pwm,200)
    right.start(0)
    left.start(0)