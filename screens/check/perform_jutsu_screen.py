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
from utils.CvDrawText import CvDrawText

class PerformJutsuScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        
        # init some Constant here
        self.DETECTION_CONFIDENCE = 0.75  # for naruto gestures
        self.DETECTION_MIN_D = 0.05  # for added gestures
        self.Hand_Detection_Confidence = 0.1
        self.Hand_Tracking_Confidence = 0.1

        # init some private varibles here
        self.font_path = FONT
        self.button_areas = []
    
    def draw(self, frame):
        frame[:] = (150, 150, 150)  # white BG

        # add title
        CvDrawText.puttext(
            frame, "招式", (10, 10), self.font_path, 48, color=(0, 0, 0)
        )
        
    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.callback("back")
                break
    
    # private methods here ------------
          
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