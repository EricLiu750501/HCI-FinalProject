import cv2
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
from utils.CvDrawText import CvDrawText
from utils.constants import WINDOW_SIZE, FONT

class PerformJutsuScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        
        # init some Constant here
        self.DETECTION_CONFIDENCE = 0.75  # for naruto gestures
        self.DETECTION_MIN_D = 0.05  # for added gestures
        self.Hand_Detection_Confidence = 0.1
        self.Hand_Tracking_Confidence = 0.1
        
        # Load labels
        with open("setting/labels.csv", encoding="utf8") as f:
            naruto_labels = csv.reader(f)
            self.naruto_labels = [row for row in naruto_labels]
            
        # Camera setup
        self.cap = cv2.VideoCapture(0)  # Open default camera
        if not self.cap.isOpened():
            print("Cannot open camera, please check the device.")
            self.cap = None
            
        # Media Pipe set up
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.Hand_Detection_Confidence,
            min_tracking_confidence=self.Hand_Tracking_Confidence,
        )
        self.drawing_utils = mp.solutions.drawing_utils
        
        # YOLOX model setup
        model_path = "model/yolox/yolox_nano.onnx"
        input_shape = (416, 416)
        score_th = 0.7
        nms_th = 0.45
        nms_score_th = 0.1

        self.yolox = YoloxONNX(
            model_path=model_path,
            input_shape=input_shape,
            class_score_th=score_th,
            nms_th=nms_th,
            nms_score_th=nms_score_th,
        )

        # init some private varibles here
        self.font_path = FONT
        self.button_areas = []
        
        self.created_gestures_d = None
        self.gesture_labels = None
        
        self.cur_jutsu = None
        self.cur_sequence_i = None
        
    # GM gonna call this public method everytime switch to this screen
    def set_jutsu(self, jutsu):
        self.cur_jutsu = jutsu
        self.cur_sequence_i = 0
        
        # since yolo model start with none, keeps consistency
        self.gesture_labels = [
            {
                "g_name_zh": None,
                "g_name_en": None
            }
        ]
        
        # reload created gestures' distances
        with open("setting/created_gestures_d.json", mode="r", encoding="utf8") as created_gestures_d:
            self.created_gestures_d = json.load(created_gestures_d)
        
        # merge naruto labels with created labels
        for i in range(1, self.created_gestures_d[len(self.created_gestures_d) - 1]["g_id"] + 1):
            if i <= 12:
                self.gesture_labels.append({
                    "g_name_zh": self.naruto_labels[i][1],
                    "g_name_en": self.naruto_labels[i][0]
                })
            else:
                self.gesture_labels.append({
                    "g_name_zh": self.created_gestures_d[i - 13]["g_name_zh"],
                    "g_name_en": self.created_gestures_d[i - 13]["g_name_en"]
                })
                
    def draw(self, frame):
        # load BG
        frame[:] = (150, 150, 150)  # white BG, will change later on
        
        if self.cur_jutsu == None:
            # not yet loaded the j_id user wants to perform
            return

        # add title
        CvDrawText.puttext(
            frame, f"施展招式: {self.cur_jutsu['name_zh']} 吧!", (10, 10), self.font_path, 40, color=(0, 0, 0)
        )
        
        # add sequence of gestures' zh name
        self.__draw_sequece(frame)
        
        # add hint image to the right
        self.__draw_hint_image(frame)
        
        # draw a seperate line
        cv2.line(frame, (700, 0), (700, WINDOW_SIZE[1]), (200, 200, 200), 2)
        
        # add cam image to the left
        
        # add buttons
        self.__draw_buttons(frame)
        
    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.callback("back")
                break
    
    # private methods here ---------------------------------------------
    
    def __draw_sequece(self, frame):
        start_x = 10
        start_y = 80
        
        blank = 50
        # big_blank = 50
        
        for g_id in self.cur_jutsu["sequence"]:
            if g_id == self.cur_jutsu["sequence"][self.cur_sequence_i]:
                color = (255, 0, 0)
            else:
                color = (0, 0, 0)
                
            if(g_id == self.cur_jutsu["sequence"][0]):
                # draw the first {gesture name}
                CvDrawText.puttext(
                    frame,
                    self.gesture_labels[g_id]["g_name_zh"],
                    (start_x, start_y),
                    self.font_path, 40, color
                )
            else:
                # draw an "→" + {gesture name}
                # for →:
                CvDrawText.puttext(
                    frame,
                    "→",
                    (start_x, start_y),
                    self.font_path, 40, color
                )
                
                start_x += blank
                
                # for {gesture name}
                CvDrawText.puttext(
                    frame,
                    self.gesture_labels[g_id]["g_name_zh"],
                    (start_x, start_y),
                    self.font_path, 40, color
                )
            
            # for spacing
            start_x += blank
            
    def __draw_hint_image(self, frame):
        gesture_img_path = f"assets/images/gesture_{self.cur_jutsu['sequence'][self.cur_sequence_i]}.jpg"
        
        if os.path.exists(gesture_img_path):
            gesture_img = cv2.imread(gesture_img_path)
            if gesture_img is not None:
                gesture_img = cv2.resize(gesture_img, (500, 500))
                frame[100:100 + 500, 750:750 + 500] = gesture_img
        
    def __draw_buttons(self, frame):
        # init some button attributes
        btn_width = 200
        btn_height = 50

        # draw back button
        back_x, back_y = 50, WINDOW_SIZE[1] - 100

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