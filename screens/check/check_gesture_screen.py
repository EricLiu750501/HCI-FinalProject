import cv2
from screens.base_screen import BaseScreen
from utils.CvDrawText import CvDrawText
import numpy as np
import os
import json
import time
import copy
import csv
from utils.constants import WINDOW_SIZE
from model.yolox.yolox_onnx import YoloxONNX


class CheckGestureScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        
        # init some private varibles here
        self.font_path = "C:/Windows/Fonts/msjh.ttc"
        self.button_areas = []
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)  # Open default camera
        if not self.cap.isOpened():
            print("Cannot open camera, please check the device.")
            self.cap = None

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
        
        # Load labels
        with open("setting/labels.csv", encoding="utf8") as f:
            labels = csv.reader(f)
            self.labels = [row for row in labels]


    def draw(self, frame):
        frame[:] = (255, 255, 255)  # white BG

        # add title
        frame[:] = CvDrawText.puttext(
            frame, "檢查手勢", (100, 100), self.font_path, 48, color=(0, 0, 0)
        )
    
        self.draw_buttons(frame)
        
    
    def draw_buttons(self, frame):
        # init some button attributes
        btn_width = 200
        btn_height = 50
        
        # draw back button
        back_x, back_y = 50, WINDOW_SIZE[1] - 100
        
        cv2.rectangle(
            frame, (back_x, back_y), (back_x + btn_width, back_y + btn_height), (0, 0, 255), -1
        )
        
        frame[:] = CvDrawText.puttext(
            frame,
            "返回",
            (back_x + 70, back_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        
        self.button_areas.append((back_x, back_y, back_x + btn_width, back_y + btn_height))
                

    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.callback("back")
                break
