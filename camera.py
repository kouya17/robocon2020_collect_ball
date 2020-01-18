import time
import picamera
import sys

with picamera.PiCamera() as camera:
    camera.resolution = (1024,768)
    camera.rotation = 180
    camera.start_preview()
    while True:
        print('waiting input file_num ...')
        num = input()
        camera.capture('../pic/picture' + num + '.jpg')
        print('saved picture' + num + '.jpg')

