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
    DEBUG_IMSHOW = DISABLE

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
    #CAMERA_RANGE_R = 170

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
        #mask_0 = np.zeros((480, 480, 1), np.uint8)
        #cv2.circle(mask_0, (self.CAMERA_CENTER_CX_T, self.CAMERA_CENTER_CY_T), self.CAMERA_RANGE_R, 255, thickness=-1)

        #if color_name == 'RED':
        # 赤色のHSVの値域1
        hsv_range_min = np.array([0, 64, 0])
        hsv_range_max = np.array([30, 255, 255])
        mask1 = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))

        # 赤色のHSVの値域2
        hsv_range_min = np.array([160, 64, 0])
        hsv_range_max = np.array([179, 255, 255])
        mask2 = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
        mask = mask1 + mask2
        #mask = mask2
        # mask = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
        #mask = cv2.bitwise_and(mask, mask, mask=mask_0)

        if self.DEBUG_IMSHOW == self.ENABLE:
            #cv2.imshow('Mask' + color_name, mask.transpose((1, 0)))
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

    # @brief 指定色の最大領域を検知する
    # @param hsv_img HSV変換後の処理対象画像
    # @param hsv_range_min 検知する色範囲の最小値
    # @param hsv_range_max 検知する色範囲の最大値
    # @param color_name 検知する色の名前
    # @detail
    def colorDetect(self, hsv_img, hsv_range_min, hsv_range_max, color_name):
        #mask_0 = np.zeros((480, 480, 1), np.uint8)
        #cv2.circle(mask_0, (self.CAMERA_CENTER_CX_T, self.CAMERA_CENTER_CY_T), self.CAMERA_RANGE_R, 255, thickness=-1)

        mask = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
        #mask = cv2.bitwise_and(mask, mask, mask=mask_0)

        if self.DEBUG_IMSHOW == self.ENABLE:
            #cv2.imshow('Mask' + color_name, mask.transpose((1, 0)))
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

    # @brief フィールド領域を検知する
    # @param hsv_img HSV変換後の処理対象画像
    # @param hsv_range_min 検知する色範囲の最小値
    # @param hsv_range_max 検知する色範囲の最大値
    # @param color_name 検知する色の名前
    # @detail
    def wallDetect(self, hsv_img, hsv_range_min, hsv_range_max, color_name):
        #mask_0 = np.zeros((480, 480, 1), np.uint8)
        #cv2.circle(mask_0, (self.CAMERA_CENTER_CX_T, self.CAMERA_CENTER_CY_T), self.CAMERA_RANGE_R, 255,
        #           thickness=-1)

        mask = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
        #mask = cv2.bitwise_and(mask, mask, mask=mask_0)
        # TODO: initに移動する
        kernel = np.zeros((self.KARNEL_SIZE, self.KARNEL_SIZE), np.uint8)
        cv2.circle(kernel, (self.KARNEL_R, self.KARNEL_R), self.KARNEL_R, 1, thickness=-1)
        mask = cv2.dilate(mask, kernel, iterations=1)

        if self.DEBUG_IMSHOW == self.ENABLE:
            #cv2.imshow('Mask' + color_name, mask.transpose((1, 0)))
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
        '''
        # TODO: cx = -1のときはどうする？
        vx = self.CAMERA_CENTER_CY - cy
        vy = self.CAMERA_CENTER_CX - cx

        try:
            ball_distance = int(hypot(vx, vy))
            ball_angle = degrees(atan2(vy, vx))
        except:
            ball_distance = -1
            ball_angle = 360
        '''

        ball_angle = cx - self.CAMERA_CENTER_CX
        ball_distance = cy + 240
        
        return int(ball_angle), int(ball_distance)

    def imageProcessingFrame(self, frame, shmem):
        # HSV色空間に変換
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #cv2.circle(frame, (self.CAMERA_CENTER_CX_T, self.CAMERA_CENTER_CY_T),
        #           self.CAMERA_RANGE_R, (0, 0, 255), thickness=1)
        cv2.line(frame, (self.CAMERA_CENTER_CX, 0), (self.CAMERA_CENTER_CX, 480),
                 (0, 0, 255), thickness=1)
        cv2.line(frame, (0, self.CAMERA_CENTER_CY), (480, self.CAMERA_CENTER_CY),
                 (0, 0, 255), thickness=1)
        '''
        # 黄色領域の検知
        yellow_cx_t, yellow_cy_t, yellow_area_size, yellow_convex = self.colorDetect(hsv_img, self.YELLOW_HSV_RANGE_MIN,
                                                                                     self.YELLOW_HSV_RANGE_MAX,
                                                                                     'Yellow')
        if yellow_cx_t > -1:
            self.draw_marker(frame, yellow_cx_t, yellow_cy_t, (30, 255, 255))

        # 青色領域の検知
        blue_cx_t, blue_cy_t, blue_area_size, blue_convex = self.colorDetect(hsv_img, self.BLUE_HSV_RANGE_MIN,
                                                                             self.BLUE_HSV_RANGE_MAX,
                                                                             'Blue')
        if blue_cx_t > -1:
            self.draw_marker(frame, blue_cx_t, blue_cy_t, (255, 30, 30))

        # 壁の検知
        field_cx_t, field_cy_t, field_area_size, field_convex = self.wallDetect(hsv_img, self.FIELD_HSV_RANGE_MIN, self.FIELD_HSV_RANGE_MAX, 'Wall')
        if field_cx_t > -1:
            cv2.drawContours(frame, [field_convex], 0, (0, 255, 0), thickness=1)
            self.draw_marker(frame, field_cx_t, field_cy_t, (0, 128, 0))
        '''

        # 赤色領域の検知
        red_cx, red_cy, red_area_size, red_convex = self.colorDetect2(hsv_img, 'Red')
        if red_cx > -1:
            self.draw_marker(frame, red_cx, red_cy, (255, 30, 30))

        #DEBUG('Yellow :' + str(yellow_area_size).rjust(8), 'Blue :' + str(blue_area_size).rjust(8))
        DEBUG('Red :' + str(red_area_size).rjust(8))

        # 画角の前後左右と画像表示の上下左右を揃えるためにx座標とy座標を交換する。
        '''
        yellow_cx = yellow_cy_t
        yellow_cy = yellow_cx_t
        blue_cx = blue_cy_t
        blue_cy = blue_cx_t
        field_cx = field_cy_t
        field_cy = field_cx_t

        yellow_cx = yellow_cx_t
        yellow_cy = yellow_cy_t
        blue_cx = blue_cx_t
        blue_cy = blue_cy_t
        field_cx = field_cx_t
        field_cy = field_cy_t
        '''
        red_cy = -red_cy

        '''
        yellow_goal_angle, yellow_goal_distance = self.calcBallDirection(yellow_cx, yellow_cy, yellow_area_size)
        blue_goal_angle, blue_goal_distance = self.calcBallDirection(blue_cx, blue_cy, blue_area_size)
        field_center_angle, field_center_distance = self.calcBallDirection(field_cx, field_cy, field_area_size)
        DEBUG('Yellow : Angle=' + str(yellow_goal_angle).rjust(4), 'Dis=' + str(yellow_goal_distance).rjust(3),
              'Blue : Angle=' + str(blue_goal_angle).rjust(4), 'Dis=' + str(blue_goal_distance).rjust(3),
              'field : Angle=' + str(field_center_angle).rjust(4), 'Dis=' + str(field_center_distance).rjust(3),)
        '''
        red_ball_angle, red_ball_distance = self.calcBallDirection(red_cx, red_cy, red_area_size)

        #return yellow_goal_angle, yellow_goal_distance, blue_goal_angle, blue_goal_distance, field_center_angle, field_center_distance
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

                    #yellow_goal_angle, yellow_goal_distance, blue_goal_angle, blue_goal_distance, field_center_angle, field_center_distance = self.imageProcessingFrame(stream.array, shmem)
                    red_ball_angle, red_ball_distance = self.imageProcessingFrame(stream.array, shmem)

                    DEBUG('red ball: angle =' + str(red_ball_angle).rjust(5) + ', distance = ' + str(red_ball_distance).rjust(5))
                    # 結果表示
                    # 画角の前後左右と画像表示の上下左右を揃えるために画像を転置する。
                    
                    if self.DEBUG_IMSHOW == self.ENABLE:
                        #cv2.imshow('Frame', stream.array.transpose((1, 0, 2)))
                        cv2.imshow('Frame', cv2.flip(stream.array, -1))
                        #cv2.imshow('Frame', stream.array)
                        cv2.moveWindow('Frame', 0, 30)
                        cv2.moveWindow('MaskRed', 482, 30)
                        #cv2.moveWindow('MaskYellow', 482, 30)
                        #cv2.moveWindow('MaskBlue', 964, 30)
                        #cv2.moveWindow('MaskWall', 482, 502)
              
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
