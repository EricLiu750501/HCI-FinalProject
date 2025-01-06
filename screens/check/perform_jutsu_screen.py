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
# from screens.check.check_gesture_screen import CheckGestureScreen
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
        self.PROGRESS_DURATION = 2 # how many second to perform a gesture
        
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
        
        self.progressing = False
        self.start_time = 0
        
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
        num_gestures = len(self.naruto_labels) - 1 + len(self.created_gestures_d)
        for i in range(1, num_gestures + 1):
            if i <= len(self.naruto_labels) - 1:
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
        if self.cur_sequence_i >= len(self.cur_jutsu["sequence"]):
            # congrats! all gestures are performed
            # free openCV cam for next usage
            self.cap.release()
            self.cap = None
            
            self.callback("show_screen", self.cur_jutsu["id"])
            return
            
        # 載入背景圖片
        background_image = cv2.imread("assets/images/JutsuPerformBG.png")
        if background_image is not None:
            # 確保背景圖片大小符合視窗大小
            background_image = cv2.resize(
                background_image, (frame.shape[1], frame.shape[0])
            )
            frame[:] = background_image
        else:
            frame[:] = (150, 150, 150)  # gray BG
        
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
        # reload cap if needed
        if self.cap == None:
            self.cap = cv2.VideoCapture(0)  # Open default camera
            if not self.cap.isOpened():
                print("Cannot open camera, please check the device.")
                self.cap = None
        
        # start showing the cam img
        ret, image = self.cap.read()
        
        if ret:
            image = cv2.flip(image, 1)
            
            # resize the cam frame to fit the frame
            frame[70 : 70 + 480, 10 : 10 + 640] = cv2.resize(image, (640, 480))
            
            result_id = self.__find_gesture_id_in_cam(image)
            
            if result_id == self.cur_jutsu["sequence"][self.cur_sequence_i]:
                if not self.progressing:
                    # start the progress of gesture performing, count {self.PROGRESS_DURATION} seconds
                    self.start_time = time.time()
                    
                    self.progressing = True
                else:
                    # count down
                    elapsed_time = time.time() - self.start_time
                    # Clamp progress to 100
                    progress = min(100, int((elapsed_time / self.PROGRESS_DURATION) * 100))
                    
                    # draw the prograss bar under the hint image
                    self.__draw_progress_bar(frame, progress)
                    
                    if progress == 100:
                        # goto the next gesture
                        self.cur_sequence_i += 1
                        
                        self.progressing = False
            else:
                # reset the progress
                self.progressing = False
                    
        
        # add buttons
        self.__draw_buttons(frame)
        
    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                # free openCV cam for next usage
                self.cap.release()
                self.cap = None
                
                self.callback("practice_screen")
                break
    
    # private methods here ---------------------------------------------
    
    def __draw_sequece(self, frame):
        start_x = 10
        start_y = WINDOW_SIZE[1] - 100
        
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
        # draw title
        CvDrawText.puttext(
            frame,
            'Hint!',
            (850, 50),
            self.font_path, 20, (0, 0, 0)
        )
        
        # draw image
        gesture_img_path = f"assets/images/gesture_{self.cur_jutsu['sequence'][self.cur_sequence_i]}.jpg"
        
        if os.path.exists(gesture_img_path):
            gesture_img = cv2.imread(gesture_img_path)
            if gesture_img is not None:
                gesture_img = cv2.resize(gesture_img, (530, 398))
                frame[100:100 + 398, 750:750 + 530] = gesture_img
          
    # draw a prograss bar with 0 ~ 100%    
    def __draw_progress_bar(self, frame, progress):       
        x = 750
        y = 550
        
        width = 200
        height = 50
        
        color_bg = (255, 255, 255)
        color_fg = (0, 0, 255)
        
        thickness = 2
        
        # Draw the outline of the progress bar
        cv2.rectangle(frame, (x, y), (x + width, y + height), color_bg, thickness)

        # Calculate the width of the filled portion
        fill_width = int((progress / 100) * width)

        # Draw the filled portion
        cv2.rectangle(frame, (x, y), (x + fill_width, y + height), color_fg, -1)
        
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
        
    # this private method is to try find a gesture id that is detected by what
    # ever ways, if didnt detect any, it returns none
    def __find_gesture_id_in_cam(self, image):
        # start from yolo model
        boxes, scores, g_ids = self.yolox.inference(
            image
        )

        # find every possible naruto gesture determined by yolo model
        for box, score, g_id in zip(boxes, scores, g_ids):
            g_id = int(g_id) + 1  # add 1 because of labels.csv starts from none

            if score < self.DETECTION_CONFIDENCE:
                # didn't detect naruto gesture in this box, go next possible box
                continue
            else:
                # find a gesture!
                return g_id
            
        # oh no.. we didnt find the g_id in yolo model
        # it's fine, find it in created gestures
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
                # find a gesture!
                return gesture_id
            
        # unfortunately, no gesture found
        return None
            
    # literally the same function in check gesture screen, but I'm lazy to deal with python inheriting
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
        if len(right_d) == 0 and len(left_d) == 0:
            return None
            
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
                
                if left_mean_d < self.DETECTION_MIN_D:
                    # congrats! we get the gesture
                    return created_gesture_d["g_id"]
                
        return None