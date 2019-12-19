# coding: UTF-8

import unittest
from imageProcessing import ImageProcessing
from ctypes import Structure, c_int, c_double
from debug import ERROR, WARN, INFO, DEBUG, TRACE
import cv2
import time
import glob

# テスト用共有メモリの構造体
class TestPoint(Structure):
    _fields_ = [('irAngle', c_int), ('isTouched', c_int), ('enemyGoalAngle', c_int), ('enemyGoalDis', c_int), ('myGoalAngle', c_int), ('myGoalDis', c_int), ('fieldCenterAngle', c_int), ('fieldCenterDis', c_int)]


if __name__ == '__main__':
    from multiprocessing import Process, Value

    TRACE('test main line')
    # テスト用共有メモリの準備
    shmem = Value(TestPoint, 0)

    # モータ制御インスタンスの生成
    imageProcessing = ImageProcessing()

    p_imageProcessing = Process(target=imageProcessing.target, args=(shmem,))

    file_list = glob.glob("./camera_distance/0degree/*jpg")
    TRACE(file_list)

    for file in file_list:
        TRACE(file)
        stream = cv2.imread(file)

        yellow_goal_angle, yellow_goal_distance, blue_goal_angle, blue_goal_distance, field_center_angle, field_center_distance = imageProcessing.imageProcessingFrame(stream, shmem)

        cv2.imshow('Frame', stream.transpose((1, 0, 2)))
        cv2.moveWindow('Frame', 0, 30)
        cv2.moveWindow('MaskYellow', 482, 30)
        cv2.moveWindow('MaskBlue', 964, 30)
        cv2.moveWindow('MaskWall', 482, 502)
        cv2.waitKey(0)

    p_imageProcessing.start()
    TRACE('p_imageProcessing started')

    cv2.destroyAllWindows()
    # p_imageProcessing.join()
