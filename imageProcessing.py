# coding: UTF-8

from enum import IntEnum
from debug import ERROR, WARN, INFO, DEBUG, TRACE

import cv2
import numpy as np
import picamera
import picamera.array
import os

from math import atan2, degrees, hypot


class ImageProcessing:
    # 画像出力の有効無効
    ENABLE = 1
    DISABLE = 0
    DEBUG_IMSHOW = ENABLE

    RED_HSV_RANGE_MIN_1 = [0, 70, 0]
    RED_HSV_RANGE_MAX_1 = [30, 255, 255]
    RED_HSV_RANGE_MIN_2 = [160, 70, 0]
    RED_HSV_RANGE_MAX_2 = [179, 255, 255]
    BLUE_HSV_RANGE_MIN = [55, 70, 10]
    BLUE_HSV_RANGE_MAX = [120, 150, 80]
    YELLOW_HSV_RANGE_MIN = [15, 127, 30]
    YELLOW_HSV_RANGE_MAX = [30, 255, 255]
    FIELD_HSV_RANGE_MIN = [42, 70, 20]
    FIELD_HSV_RANGE_MAX = [60, 240, 100]
    FIELD_AND_WALL_HSV_RANGE_MIN = [25, 70, 0]
    FIELD_AND_WALL_RANGE_MAX = [120, 255, 255]

    CAMERA_CENTER_CX = 240
    CAMERA_CENTER_CY = 240
    # CAMERA_RANGE_R = 170

    KARNEL_R = 4
    KARNEL_SIZE = 2 * KARNEL_R + 1

    GOAL_DISTANCE_TABLE = []

    # @brief コンスタラクタ
    # @detail 初期化処理を行う
    def __init__(self):
        TRACE('ImageProcessing generated')

        # テーブルの読み込み
        # TODO: テーブル情報は仮。csvファイルから読み込むようにする
        self.GOAL_DISTANCE_TABLE = range(241)
    
    # @brief 指定色の最大領域を検知する
    # @param hsv_img HSV変換後の処理対象画像
    # @param color_name 検知する色の名前
    # @detail
    def colorDetect2(self, hsv_img, color_name):

        if color_name == 'RED':
            # 赤色のHSVの値域1
            hsv_range_min = self.RED_HSV_RANGE_MIN_1
            hsv_range_max = self.RED_HSV_RANGE_MAX_1
            mask1 = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))

            # 赤色のHSVの値域2
            hsv_range_min = self.RED_HSV_RANGE_MIN_2
            hsv_range_max = self.RED_HSV_RANGE_MAX_2
            mask2 = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
            mask = mask1 + mask2
        elif color_name == 'YELLOW':
            hsv_range_min = self.YELLOW_HSV_RANGE_MIN
            hsv_range_max = self.YELLOW_HSV_RANGE_MAX
            mask = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
            
        if self.DEBUG_IMSHOW == self.ENABLE:
            cv2.imshow('Mask' + color_name, cv2.flip(mask, -1))

        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        convex_hull_list = []
        for contour in contours:
            approx = cv2.convexHull(contour)

            M = cv2.moments(approx)
            convex_hull_list.append({'approx': approx, 'moment': M})

        if len(convex_hull_list) > 0:
            max_convex_hull = max(convex_hull_list, key=(lambda x: x['moment']['m00']))
            if max_convex_hull['moment']['m00'] > 0:
                area_size = max_convex_hull['moment']['m00']

                cx = int(max_convex_hull['moment']['m10'] / max_convex_hull['moment']['m00'])
                cy = int(max_convex_hull['moment']['m01'] / max_convex_hull['moment']['m00'])

                return cx, cy, area_size, max_convex_hull['approx']
            return -1, -1, 0.0, []
        else:
            return -1, -1, 0.0, []

    # @brief フィールド領域を検知する
    # @param hsv_img HSV変換後の処理対象画像
    # @param hsv_range_min 検知する色範囲の最小値
    # @param hsv_range_max 検知する色範囲の最大値
    # @param color_name 検知する色の名前
    # @detail
    def wallDetect(self, hsv_img, hsv_range_min, hsv_range_max, color_name):
        mask = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
        # TODO: initに移動する
        kernel = np.zeros((self.KARNEL_SIZE, self.KARNEL_SIZE), np.uint8)
        cv2.circle(kernel, (self.KARNEL_R, self.KARNEL_R), self.KARNEL_R, 1, thickness=-1)
        mask = cv2.dilate(mask, kernel, iterations=1)

        if self.DEBUG_IMSHOW == self.ENABLE:
            cv2.imshow('Mask' + color_name, mask)

        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        convex_hull_list = []
        for contour in contours:
            approx = cv2.convexHull(contour)

            M = cv2.moments(approx)
            convex_hull_list.append({'approx': approx, 'moment': M})

        if len(convex_hull_list) > 0:
            max_convex_hull = max(convex_hull_list, key=(lambda x: x['moment']['m00']))
            if max_convex_hull['moment']['m00'] > 0:
                area_size = max_convex_hull['moment']['m00']

                cx = int(max_convex_hull['moment']['m10'] / max_convex_hull['moment']['m00'])
                cy = int(max_convex_hull['moment']['m01'] / max_convex_hull['moment']['m00'])

                return cx, cy, area_size, max_convex_hull['approx']
            return -1, -1, 0.0, []
        else:
            return -1, -1, 0.0, []

    # @brief 十字マーカーを描画する
    # @param x 十字マーカーのx座標
    # @param y 十字マーカーのy座標
    # @param marker_color 十字マーカーの色
    def draw_marker(self, img, x, y, marker_color):
        cv2.line(img, (x - 7, y), (x + 7, y), color=(255, 255, 255), thickness=2)
        cv2.line(img, (x, y - 7), (x, y + 7), color=(255, 255, 255), thickness=2)
        cv2.line(img, (x - 7, y), (x + 7, y), color=marker_color, thickness=1)
        cv2.line(img, (x, y - 7), (x, y + 7), color=marker_color, thickness=1)

    # @brief 画像処理によって検知した領域からボールの方向と距離を計算する
    # @param cx 領域のx座標
    # @param cy 領域のy座標
    # @param area_size 領域の面積
    def calcBallDirection(self, cx, cy, area_size):
        ball_angle = cx - self.CAMERA_CENTER_CX
        ball_distance = cy + 240
        
        return int(ball_angle), int(ball_distance)

    def imageProcessingFrame(self, frame, shmem):
        # HSV色空間に変換
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.line(frame, (self.CAMERA_CENTER_CX, 0), (self.CAMERA_CENTER_CX, 480),
                 (0, 0, 255), thickness=1)
        cv2.line(frame, (0, self.CAMERA_CENTER_CY), (480, self.CAMERA_CENTER_CY),
                 (0, 0, 255), thickness=1)
        '''
        # 壁の検知
        field_cx_t, field_cy_t, field_area_size, field_convex = self.wallDetect(hsv_img, self.FIELD_HSV_RANGE_MIN, self.FIELD_HSV_RANGE_MAX, 'Wall')
        if field_cx_t > -1:
            cv2.drawContours(frame, [field_convex], 0, (0, 255, 0), thickness=1)
            self.draw_marker(frame, field_cx_t, field_cy_t, (0, 128, 0))
        '''

        # 赤色領域の検知
        red_cx, red_cy, red_area_size, red_convex = self.colorDetect2(hsv_img, 'RED')
        if red_cx > -1:
            self.draw_marker(frame, red_cx, red_cy, (255, 30, 30))
        
        # 黄色領域の検知
        yellow_cx, yellow_cy, yellow_area_size, yellow_convex = self.colorDetect2(hsv_img, 'YELLOW')
        if yellow_cx > -1:
            self.draw_marker(frame, yellow_cx, yellow_cy, (30, 255, 255))

        DEBUG('Red :' + str(red_area_size).rjust(8))
        DEBUG('Yellow :' + str(yellow_area_size).rjust(8))

        # 画角の前後左右と画像表示の上下左右を揃えるためにx座標とy座標を交換する。
        red_cy = -red_cy
        yellow_cy = -yellow_cy

        red_ball_angle, red_ball_distance = self.calcBallDirection(red_cx, red_cy, red_area_size)

        return red_ball_angle, red_ball_distance

    # @brief 画像処理のmain処理
    # @param shmem 共有メモリ
    def imageProcessingMain(self, shmem):
        # 画像処理を行う

        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as stream:
                camera.resolution = (480, 480)
                cap = cv2.VideoCapture(0)

                while cap.isOpened():
                    # 画像を取得し、stream.arrayにRGBの順で映像データを格納
                    camera.capture(stream, 'bgr', use_video_port=True)

                    red_ball_angle, red_ball_distance = self.imageProcessingFrame(stream.array, shmem)

                    DEBUG('red ball: angle =' + str(red_ball_angle).rjust(5) + ', distance = ' + str(red_ball_distance).rjust(5))
                    
                    # 結果表示
                    # 画角の前後左右と画像表示の上下左右を揃えるために画像を転置する。
                    if self.DEBUG_IMSHOW == self.ENABLE:
                        cv2.imshow('Frame', cv2.flip(stream.array, -1))
                        cv2.moveWindow('Frame', 0, 30)
                        cv2.moveWindow('MaskRED', 482, 30)
                        cv2.moveWindow('MaskYELLOW', 964, 30)
              
                    # 共有メモリに書き込む
                    shmem.ballAngle = int(red_ball_angle * 90 / 240)
                    shmem.ballDis = int(red_ball_distance)

                    # "q"でウィンドウを閉じる
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                    # streamをリセット
                    stream.seek(0)
                    stream.truncate()
                cv2.destroyAllWindows()

    def target(self, shmem):
        TRACE('imageProcessingMain target() start')
        self.imageProcessingMain(shmem)

    def close():
        pass
