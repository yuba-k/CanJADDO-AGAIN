# -*- coding: utf-8 -*-

###
#このコードを用いる場合、引数として写真の縦横のピクセル数を与える
###

import picamera

def	cap(HEIGHT,WIDTH):
    with picamera.PiCamera() as	camera:
        camera.exposure_mode = 'off' #露出モード 
        camera.meter_mode = 'average' #測光モード
        camera.resolution=(WIDTH,HEIGHT)
        camera.start_preview()
        camera.capture(f'picture.jpg')