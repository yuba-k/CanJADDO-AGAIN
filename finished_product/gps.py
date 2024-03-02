import time
import math
import serial
import adafruit_gps
import sys
import RPi.GPIO as GPIO
import logging
import signal

# #log settings
# logging.basicConfig(level=logging.INFO)#ログレベルの設定
# logger=logging.getLogger('GPS_phase')#ログの名前
# formatter=logging.Formatter('%(asctime)s:	%(filename)s:	%(lineno)d:	%(levelname)s:	%(message)s')#実行時間
# file_handler=logging.FileHandler('history.log',	encoding='utf-8')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

#ログの設定の読み込み
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

def main():
    duty = 50
    sec = 8

    #ゴールの座標をここに入力！
    coordinate_goal = {'lat':31.731461, 'lon':130.726171}
    logger.info(f"coordinate_goal:{coordinate_goal}")
    
    init()
    coordinate_new = get_gpsdata()
    while not gps.has_fix:  #GPSデータの取得待ち...     Loading...
        print("Waiting for fix...")
        time.sleep(1)
        coordinate_new = get_gpsdata()
        logger.info(f"{coordinate_new}")
    move("straight", duty, sec) #とりあえずsec秒前進．前へすすめー！

    while True:
        coordinate_old = coordinate_new
        coordinate_new = get_gpsdata()
        while(coordinate_old.latitude == coordinate_new.latitude and
           coordinate_old.longitude == coordinate_new.longitude):
            coordinate_new = get_gpsdata()  #前回と今回のGPSデータが同一だった場合，新規取得
        logger.info(f"{coordinate_new}")
        
        if not gps.has_fix or coordinate_new['lat'] is None:
            print("Waiting for fix...")
            continue
        
        #以下，北を0度として考える．
        #ゴールと機体の位置を結ぶベクトルの角度を計算する．西がマイナス，東がプラス
        coordinate_diff_goal = { 'lat' : (coordinate_goal['lat'] - coordinate_new['lat']), 
                            'lon' : (coordinate_goal['lon'] - coordinate_new['lon'])}
        degree_for_goal = math.atan2(
                coordinate_diff_goal['lon'], coordinate_diff_goal['lat']) / math.pi * 180
        
        #機体が動いた経路の角度を計算する．
        #TODO GPSデータに移動経路の方角が含まれている？ 要検証
        coordinate_diff_me = { 'lat' : (coordinate_new['lat'] - coordinate_old['lat']), 
                            'lon' : (coordinate_new['lon'] - coordinate_old['lon'])}
        degree_for_me = math.atan2(
                coordinate_diff_me['lon'], coordinate_diff_me['lat']) / math.pi * 180
        
        #ゴールの角度から機体が動いた角度を引き，機体から見たゴールの角度を計算する．
        #このとき，機体前方を0度とし，左がマイナス，右がプラス
        degree = degree_for_goal-degree_for_me
        degree = (degree + 360) if (degree < -180) else degree
        degree = (degree - 360) if (180 < degree) else degree

        #目標と現在位置との距離を三平方より導出
        distance=math.sqrt(coordinate_diff_goal['lat']**2+coordinate_diff_goal['lon']**2)
        if distance<=0.005:
            return 0#距離が0.005km(5m)以下になったらGPSフェーズ終了
        
        logger.info(f"距離{distance}")
        print("{:.3f}".format(degree))

        if degree <= -45:
             move("left", duty, 4*degree/180)   #角度が大きければ大きいほど，曲がる量を多く
             move("straight", duty, sec)
        elif degree >= 45:
             move("right", duty, 4*degree/180)
             move("straight", duty, sec)
        else :#+-45
             move("straight", duty, sec)

# sample
#            move("right", duty, sec)
#            move("straight", duty, sec)
#            move("left", duty, sec)

def init():
    #GPIO configulation
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    GPIO.setup(26, GPIO.OUT)

    global right, left
    right = GPIO.PWM(13, 200)       #PWMの周波数は必ず100以上！！ 100未満にすると1パルスにおけるタイヤを動かす負荷が大きく，
    left = GPIO.PWM(26, 200)        #モータードライバが担う電流量や電力量が過度に増加．波形や動きが不安定に！！
    right.start(0)
    left.start(0)
    
    #GPS initialization
    global uart
    uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)
    signal.signal(signal.SIGINT, signal_handler)
    global gps
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    #GPRMCとGPGGAを取得．
    gps.send_command(b"PMTK220,1000")
    #出力頻度は1000[ms]間隔

def get_gpsdata(): 
    uart.reset_input_buffer()   #シリアル通信のバッファ消去
    time.sleep(1)
    gps.update()
    return {'lat':gps.latitude, 'lon':gps.longitude}

def signal_handler(sig, frame):
    print("\nExiting the program.")
    sys.exit(0)

def move(direction, duty, sec):
    t_end = time.time()
    right_ph = GPIO.output(11, GPIO.LOW)
    left_ph = GPIO.output(19, GPIO.LOW)
    right_duty = left_duty = duty

    logger.info(f"duty:{duty}")
    if direction == "right":    #右に曲がる
        logger.info(f"right")
        right_duty *= 0.6       #右足を弱く
#	    left_duty = duty
        
    elif direction == "left":   #左に曲がる
        logger.info(f"left")
#       right_duty = duty
        left_duty *= 0.6        #左足を弱く
        
    elif direction == "straight":   #まっすぐ
        logger.info(f"straight")
#       right_duty = duty
#	    left_duty = duty
        
    while time.time() <= t_end + sec:   #実際に動く
        right.ChangeDutyCycle(right_duty)
        left.ChangeDutyCycle(left_duty)
        
    right.ChangeDutyCycle(0)
    left.ChangeDutyCycle(0)
    time.sleep(2)   #モータードライバのオーバーヒート対策