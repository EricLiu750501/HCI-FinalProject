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


class CheckGestureScreen(BaseScreen):
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

        # Load labels
        with open("setting/labels.csv", encoding="utf8") as f:
            labels = csv.reader(f)
            self.labels = [row for row in labels]

    def draw(self, frame):
        frame[:] = (150, 150, 150)  # white BG

        # add title
        CvDrawText.puttext(
            frame, "檢查手勢", (10, 10), self.font_path, 48, color=(0, 0, 0)
        )

        # start showing the cam frame
        ret, image = self.cap.read()

        if ret:
            image = cv2.flip(image, 1)
            detected_naruto = False

            boxes, scores, g_ids = self.yolox.inference(
                image
            )  # g_ids stands for gesture ids

            # find every possible naruto gesture determined by yolo model
            for box, score, g_id in zip(boxes, scores, g_ids):
                g_id = int(g_id) + 1  # add 1 because of labels.csv starts from none
                detected_naruto = False

                if score < self.DETECTION_CONFIDENCE:
                    # didn't detect naruto gesture in this box, go next possible box
                    continue
                else:
                    detected_naruto = True

                # draw result in cap image
                x1, y1 = int(box[0]), int(box[1])
                x2, y2 = int(box[2]), int(box[3])

                cv2.putText(
                    image,
                    f"{self.labels[g_id][0]} {score:.3f}",
                    (x1, y1 - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    2,
                    cv2.LINE_AA,
                )

                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # draw result in frame
                start_x = 350
                start_y = WINDOW_SIZE[1] - 90

                CvDrawText.puttext(
                    frame,
                    f"Gesture's ID: {g_id}, Gesture's Name: {self.labels[g_id][1]}, Confidence: {score:.3f}",
                    (start_x, start_y),
                    self.font_path,
                    30,
                    (0, 0, 0),
                )

            # see if we find naruto gestures, if not, try find in created gestures
            if not detected_naruto:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_image)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.drawing_utils.draw_landmarks(
                            image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )

            # resize the cam frame to fit the frame
            frame[70 : 70 + 480, 300 : 300 + 640] = cv2.resize(image, (640, 480))

        # draw buttons
        self.__draw_buttons(frame)

    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.callback("back")
                break

    # Private methods here ---------------------

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
