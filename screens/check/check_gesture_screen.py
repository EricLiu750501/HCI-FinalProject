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

class CheckGestureScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)

        # init some Constant here
        self.DETECTION_CONFIDENCE = 0.75  # for naruto gestures
        self.DETECTION_MIN_D = 0.03  # for added gestures
        self.Hand_Detection_Confidence = 0.8
        self.Hand_Tracking_Confidence = 0.8

        # init some private varibles here
        self.font_path = FONT
        self.button_areas = []
        
        # Load labels
        with open("setting/labels.csv", encoding="utf8") as f:
            labels = csv.reader(f)
            self.labels = [row for row in labels]
        
        # set a flag to track if this is user's first time checking gesture
        self.first_time_check = True
        self.created_gestures_d = None
            
        # Camera setup
        # self.cap = None
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


    def draw(self, frame):
        frame[:] = (150, 150, 150)  # gray BG

        # add title
        CvDrawText.puttext(
            frame, "檢查手勢", (10, 10), self.font_path, 48, color=(0, 0, 0)
        )

        # reload cap if needed
        if self.cap == None:
            self.cap = cv2.VideoCapture(0)  # Open default camera
            if not self.cap.isOpened():
                print("Cannot open camera, please check the device.")
                self.cap = None
            
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

                if results.multi_hand_landmarks and results.multi_handedness:
                    right_hand_raw = []
                    left_hand_raw = []
                    
                    for hand_landmarks, handedness in zip(
                        results.multi_hand_landmarks, results.multi_handedness
                    ):
                        # for each hand
                        
                        # save raw points for each hand
                        landmarks = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
                        hand_label = handedness.classification[0].label  # "Left" or "Right"
                        
                        if hand_label == "Right":
                            right_hand_raw = landmarks
                        elif hand_label == "Left":
                            left_hand_raw = landmarks
                            
                    [right_d, left_d] = self.__get_current_gesture_d(right_hand_raw, left_hand_raw)
                    
                    gesture_id = self.__check_current_gesture(right_d, left_d)
                    
                    if gesture_id != None:
                        # Congrats! find the gesture, draw & display it
                        
                        # draw the result of lms in cap image first
                        for hand_landmarks in results.multi_hand_landmarks:
                            self.drawing_utils.draw_landmarks(
                                image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                            )
                            
                        # display result to screen
                        start_x = 350
                        start_y = WINDOW_SIZE[1] - 90

                        CvDrawText.puttext(
                            frame,
                            f"Gesture's ID: {gesture_id}, Gesture's Name: {self.created_gestures_d[gesture_id - 13]['g_name_zh']}",
                            (start_x, start_y),
                            self.font_path,
                            30,
                            (0, 0, 0),
                        )
                        
                        # reset gesture_id
                        gesture_id = None

            # resize the cam frame to fit the frame
            frame[70 : 70 + 480, 300 : 300 + 640] = cv2.resize(image, (640, 480))

        # draw buttons
        self.__draw_buttons(frame)

    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                # free openCV cam for next usage
                self.cap.release()
                self.cap = None
                
                # reset flags so the next time we reload the JSON
                self.first_time_check = True
                
                self.callback("back")
                break
            
    def release_cap(self):
        self.cap.release()

    # Private methods here --------------------------------------

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

    def __get_current_gesture_d(self, right_hand_raw, left_hand_raw):
        # Goal is to get all lm's distance from (ID = 0)'s lm (the palm)
        # from MediaPipe the lm for palm is the first point in our raw data
        
        # Right Hand:
        distance_right = []
        if right_hand_raw != []:
            base_point_right = np.array(right_hand_raw[0])
            
            for i, point in enumerate(right_hand_raw):
                if i != 0:
                    distance_right.append(np.linalg.norm(np.array(point) - base_point_right))
                
        # Left Hand:
        distance_left = []
        if left_hand_raw != []:
            base_point_left = np.array(left_hand_raw[0])
            
            for i, point in enumerate(left_hand_raw):
                if i != 0:
                    distance_left.append(np.linalg.norm(np.array(point) - base_point_left))
        
        
        return [distance_right, distance_left]
    
    def __check_current_gesture(self, right_d, left_d):
        # Mediapipe will bug out at line 138
        # there are no hands on the screen but it says there are...
        # Consequently, divide by 0 error occurs, adding this if statement to protect
        if len(right_d) == 0 and len(left_d) == 0:
            return None
        
        # re-load the file in case user added new gestures (if necessery)
        if self.first_time_check:
            with open("setting/created_gestures_d.json", mode="r", encoding="utf8") as created_gestures_d:
                self.created_gestures_d = json.load(created_gestures_d)
            
            self.first_time_check = False
            
        for created_gesture_d in self.created_gestures_d:
            # for each created gesture
            right_mean_d = 0
            left_mean_d = 0
            
            if created_gesture_d["right_d"] != [] and created_gesture_d["left_d"] != []:
                # Both hands comparation
                # right hand part:
                if len(right_d) == 0:
                    # user currently doesnt use right hand, goto next sample
                    continue
                
                for sample_d, cur_d in zip(created_gesture_d["right_d"], right_d):
                    # compare
                    right_mean_d += abs(sample_d - cur_d)
                    
                # left hand part:
                if len(left_d) == 0:
                    # user currently doesnt use left hand, goto next sample
                    continue
                
                for sample_d, cur_d in zip(created_gesture_d["left_d"], left_d):
                    # compare
                    left_mean_d += abs(sample_d - cur_d)
                    
                # take mean
                right_mean_d /= len(right_d)
                left_mean_d /= len(left_d)
                
                # print(f"right: {right_mean_d}")
                # print(f"left: {left_mean_d}")
                
                if right_mean_d < self.DETECTION_MIN_D and left_mean_d < self.DETECTION_MIN_D:
                    # congrats! we get the gesture
                    return created_gesture_d["g_id"]
            elif created_gesture_d["left_d"] == []:
                # right hand only:
                if len(right_d) == 0:
                    # user currently doesnt use right hand, goto next sample
                    continue
                
                for sample_d, cur_d in zip(created_gesture_d["right_d"], right_d):
                    # compare
                    right_mean_d += abs(sample_d - cur_d)
                    
                
                # take mean
                right_mean_d /= len(right_d)
                
                # print(f"right: {right_mean_d}")
                
                if right_mean_d < self.DETECTION_MIN_D:
                    # congrats! we get the gesture
                    return created_gesture_d["g_id"]
            else:                                
                # left hand only:
                if len(left_d) == 0:
                    # user currently doesnt use right hand, goto next sample
                    continue
                
                for sample_d, cur_d in zip(created_gesture_d["left_d"], left_d):
                    # compare
                    left_mean_d += abs(sample_d - cur_d)
                    
                # take mean
                left_mean_d /= len(left_d)
                
                # print(f"left: {left_mean_d}")
                
                if left_mean_d < self.DETECTION_MIN_D:
                    # congrats! we get the gesture
                    return created_gesture_d["g_id"]
                
        return None
