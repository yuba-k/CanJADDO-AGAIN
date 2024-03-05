# -*- coding: utf-8 -*-

###
#このコードを用いる場合、引数として写真の縦横のピクセル数を与える
###

import picamera
import logging.config

def	cap(HEIGHT,WIDTH):
    #ログの設定の読み込み
#    logging.config.fileConfig('logging.ini')
    logger = logging.getLogger(__name__)
    try:
        with picamera.PiCamera() as	camera:
            camera.exposure_mode = 'auto' #露出モード 
            camera.meter_mode = 'average' #測光モード
            camera.resolution=(WIDTH,HEIGHT)
            camera.start_preview()
            camera.capture(f'picture.jpg')
    except picamera.exc.PiCameraError:
        logging.error("picamera does not work")
        return 0