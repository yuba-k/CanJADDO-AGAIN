import time
import math
import board
import serial
import adafruit_gps
import sys
import RPi.GPIO as GPIO
import picamera
import logging.config
import signal

# #log settings
# logging.basicConfig(level=logging.INFO)#ログレベルの設定
# logger=logging.getLogger('GPS')#ログの名前
# formatter=logging.Formatter('%(asctime)s:	%(filename)s:	%(lineno)d:	%(levelname)s:	%(message)s')#実行時間
# file_handler=logging.FileHandler('/home/pi/sample/history.log',	encoding='utf-8')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

def main():
    duty = 80
    sec = 30

    coordinate_goal = {'lat':31.731461, 'lon':130.726171}
    logger.info(f"coordinate_goal:{coordinate_goal}")
    
    init()
    coordinate_new = get_gpsdata()
    while not gps.has_fix or coordinate_new['lat'] is None:
        print("Waiting for fix...")
        time.sleep(1)
        coordinate_new = get_gpsdata()
        logger.info(f"{coordinate_new}")
    move("straight", duty, sec)

    while True:
        coordinate_old = coordinate_new
        coordinate_new = get_gpsdata()
        logger.info(f"{coordinate_new}")
        if not gps.has_fix or coordinate_new['lat'] is None:
            print("Waiting for fix...")
            continue
        coordinate_diff_goal = { 'lat' : (coordinate_goal['lat'] - coordinate_new['lat']), 
                            'lon' : (coordinate_goal['lon'] - coordinate_new['lon'])}
        coordinate_diff_me = { 'lat' : (coordinate_new['lat'] - coordinate_old['lat']), 
                            'lon' : (coordinate_new['lon'] - coordinate_old['lon'])}
#            print(coordinate_diff)
        degree_for_goal = math.atan2(
                coordinate_diff_goal['lon'], coordinate_diff_goal['lat']) / math.pi * 180
        degree_for_me = math.atan2(
                coordinate_diff_me['lon'], coordinate_diff_me['lat']) / math.pi * 180
        degree = degree_for_goal-degree_for_me
        #目標と現在位置との距離を三平方より導出
        distance=math.sqrt(coordinate_diff_goal['lat']**2+coordinate_diff_goal['lon']**2)
        if distance<=0.005:
            return 0#距離が0.005km(5m)以下になったらGPSフェーズ終了
        print("{:.3f}".format(degree))

        if degree <= -45:
            move("left", duty, sec)
        elif degree >= 45:
            move("right", duty, sec)
        else :#+-45
            move("straight", duty, sec)

def init():
    #GPIO configulation
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    GPIO.setup(26, GPIO.OUT)

    global right, left
    right = GPIO.PWM(13, 50)
    left = GPIO.PWM(26 , 50)
    right.start(0)
    left.start(0)
    

    
    #GPS initialization
    uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)
    signal.signal(signal.SIGINT, signal_handler)
    global gps
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b"PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")

def get_gpsdata():
    gps.update()
    return {'lat':gps.latitude, 'lon':gps.longitude}

def signal_handler(sig, frame):
    print("\nExiting the program.")
    sys.exit(0)

def move(direction, duty, sec):
    t_end = time.time()
    right_ph = GPIO.output(22, GPIO.LOW)
    left_ph = GPIO.output(24, GPIO.LOW)

    if direction == "right":
        logger.info(f"duty:{duty}")
        logger.info(f"right")
        while time.time() <= t_end + sec:
            right.ChangeDutyCycle(duty*0.95)
            left.ChangeDutyCycle(duty)
    elif direction == "left":
        logger.info(f"duty:{duty}")
        logger.info(f"right")
        while time.time() <= t_end + sec:
            right.ChangeDutyCycle(duty*0.95)
            left.ChangeDutyCycle(0)
    elif direction == "straight":
        logger.info(f"duty:{duty}")
        logger.info(f"right")
        while time.time() <= t_end + sec:
            right.ChangeDutyCycle(duty)
            left.ChangeDutyCycle(duty)
