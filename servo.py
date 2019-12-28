# coding: UTF-8

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

#GPIO4を制御パルスの出力に設定
gp_out = 4
GPIO.setup(gp_out, GPIO.OUT)

#「GPIO4出力」でPWMインスタンスを作成する。
#GPIO.PWM( [ピン番号] , [周波数Hz] )
#SG92RはPWMサイクル:20ms(=50Hz), 制御パルス:0.5ms〜2.4ms, (=2.5%〜12%)。
servo = GPIO.PWM(gp_out, 50)

#パルス出力開始。　servo.start( [デューティサイクル 0~100%] )
#とりあえずゼロ指定だとサイクルが生まれないので特に動かないっぽい？
servo.start(0)
#time.sleep(1)

servo.ChangeDutyCycle(7.25)
current_duty = 7.25
target_duty = 12
duration = 3
diff_t = 0.1
count = int(duration / diff_t)
for i in range(count):
    #デューティサイクルの値を変更することでサーボが回って角度が変わる。
    #servo.ChangeDutyCycle(2.5)
    #time.sleep(0.5)

    servo.ChangeDutyCycle(current_duty + ((i + 1) * ((target_duty - current_duty) / count)))
    time.sleep(diff_t)

    #servo.ChangeDutyCycle(12)
    #time.sleep(0.5)

    #servo.ChangeDutyCycle(7.25)
    #time.sleep(0.5)

servo.stop()
GPIO.cleanup()
