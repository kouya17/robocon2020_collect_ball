# coding: UTF-8

import RPi.GPIO as GPIO
import time
from debug import ERROR, WARN, INFO, DEBUG, TRACE


class Servo:
    def __init__(self, pin_no):
        TRACE('Servo generated pin=' + str(pin_no))
        self._pin_no = pin_no
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin_no, GPIO.OUT)
        # PWMインスタンスを作成する。
        # GPIO.PWM( [ピン番号] , [周波数Hz] )
        # SG92RはPWMサイクル:20ms(=50Hz), 制御パルス:0.5ms〜2.4ms, (=2.5%〜12%)。
        self._servo = GPIO.PWM(self._pin_no, 50)
        # パルス出力開始。　servo.start( [デューティサイクル 0~100%] )
        # とりあえずゼロ指定だとサイクルが生まれないので特に動かないっぽい？
        #self._servo.start(7.25)
        self._servo.start(0)
        self._current_duty = 7.25
    
    def write(self, target_duty, duration, diff_t):
        count = int(duration / diff_t)
        for i in range(count):
            # デューティサイクルの値を変更することでサーボが回って角度が変わる。
            self._servo.ChangeDutyCycle(self._current_duty + ((i + 1) * ((target_duty - self._current_duty) / count)))
            time.sleep(diff_t)
        
        self._current_duty = target_duty
    
    def __del__(self):
        self._servo.stop()
        GPIO.cleanup()
