# coding: UTF-8

import FaBo9Axis_MPU9250
import time
from debug import DEBUG, TRACE


class Imu:
    """
    
    IMU driver class
    
    """
    
    def __init__(self, update_interval_sec=0.1):
        TRACE('Imu generated')
        self._mpu9250 = FaBo9Axis_MPU9250.MPU9250()
        self._epsilon = 0
        self._degree = 0
        self._update_interval_sec = update_interval_sec
    
    def calibrate(self, sec=5, interval_sec=0.1):
        DEBUG('Imu.calibrate() start')
        count = int(sec / interval_sec)
        sum = 0
        for i in range(count):
            gyro = self._mpu9250.readGyro()
            sum += gyro["z"]
        self._epsilon = sum / count
    
    def reset(self):
        self._degree = 0
    
    def update_loop(self, shmem):
        while 1:
            gyro = self._mpu9250.readGyro()
            self._degree += gyro["z"] - self._epsilon
            shmem.bodyAngle = int(self._degree)
            DEBUG('bodyAngle = ', shmem.bodyAngle)
            time.sleep(self._update_interval_sec)
            
    def target(self, shmem):
        DEBUG('Imu target() start')
        self.update_loop(shmem)
    
    def close(self):
        pass
