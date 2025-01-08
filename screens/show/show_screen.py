import cv2
import pygame
import mediapipe as mp
import numpy as np
import os
import json
import time
import copy
import csv
from model.yolox.yolox_onnx import YoloxONNX

# custom packages
from screens.base_screen import BaseScreen
# from screens.check.check_gesture_screen import CheckGestureScreen
from utils.CvDrawText import CvDrawText
from utils.constants import WINDOW_SIZE, FONT


class ShowScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        
        # init some Constant here
        self.DISPLAY_INTERVAL = 0.8  # in second
        self.font_path = "assets/fonts/NotoSansTC-VariableFont_wght.ttf"
        self.play_sound = pygame.mixer.Sound("assets/sounds/playsound.mp3")
        
        # init some private variables
        self.jutsu = None
        self.display_done = False
        self.sound_played = False
        
        self.cap = None
        self.cur_g_index = None
        self.start_time = None
        
        self.button_areas = []

    def set_jutsu(self, jutsu):
        self.jutsu = jutsu
        self.display_done = False
        self.sound_played = False
        
        if jutsu["id"] > 6:
            self.cur_g_index = -1  # for displaying the 1st frame in __display_consequtive
            self.start_time = time.time() - self.DISPLAY_INTERVAL

    def draw(self, frame):
        frame[:] = (50, 50, 50)  # 深灰色背景
        
        # start playing video or consequtive frames
        if not self.display_done:
            if self.jutsu["id"] <= 6:
                # display default video
                self.__display_video(frame)
            else:
                # display custom consequtive cam images
                self.__display_consequtive_images(frame)
        else:
            # show titles and play sound
            
            # 添加標題
            CvDrawText.puttext(
                frame,
                f"{self.jutsu['name_zh']}",
                (100, 100),
                self.font_path,
                48,
                color=(255, 255, 255),
            )
            
            if not self.sound_played:
                # play sound
                pygame.mixer.Sound.play(self.play_sound)

                self.sound_played = True
                
        # draw back button
        self.__draw_buttons(frame)

    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.callback("back")
                break
            
    # Private methods here-------------------------------------------
    
    def __display_video(self, frame):
        if self.cap == None:
            # start playing video
            self.cap = cv2.VideoCapture(f"assets/video/jutsu_{self.jutsu['id']}.mp4")
            if not self.cap.isOpened():
                print("Cannot read mp4, please check the device.")
                self.cap = None

        if self.cap.isOpened():
             ret, video_frame = self.cap.read()

             if ret:
                 frame[100 : 100 + 480, 300 : 300 + 640] = cv2.resize(video_frame, (640, 480))
             else:
                 # finish playing the video
                self.cap.release()
                self.cap = None
            
                self.display_done = True
        else:
            # finish playing the video
            self.cap.release()
            self.cap = None
            
            self.display_done = True
            
    def __display_consequtive_images(self, frame):
        if self.cur_g_index >= len(self.jutsu["sequence"]):
            # finish delplay
            self.display_done = True
            return
        
        if self.jutsu["sequence"][self.cur_g_index] <= 12:
            img_path = f"assets/images/temp_naruto_gestures/gesture_{self.jutsu['sequence'][self.cur_g_index]}.jpg"
        else:
            img_path = f"assets/images/gesture_{self.jutsu['sequence'][self.cur_g_index]}.jpg"
            
        # keep displaying the current gesture
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            if img is not None:
                frame[100 : 100 + 480, 300 : 300 + 640] = cv2.resize(img, (640, 480))

        if time.time() - self.start_time >= self.DISPLAY_INTERVAL:
            # goto next gesture
            self.cur_g_index += 1
                    
            # reset timer to count down
            self.start_time = time.time()
    
    def __draw_buttons(self, frame):
        # init some button attributes
        btn_width = 200
        btn_height = 50

        # draw back button
        back_x, back_y = WINDOW_SIZE[0] - 300, WINDOW_SIZE[1] - 100

        cv2.rectangle(
            frame,
            (back_x, back_y),
            (back_x + btn_width, back_y + btn_height),
            (0, 0, 255),
            -1,
        )

        CvDrawText.puttext(
            frame,
            "返回",
            (back_x + 70, back_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )

        self.button_areas.append(
            (back_x, back_y, back_x + btn_width, back_y + btn_height)
        )
