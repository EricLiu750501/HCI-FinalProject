import cv2 as cv2
import mediapipe as mp
import numpy as np
import copy
import os
import json
from utils.constants import WINDOW_SIZE

# Declare some Constant for testing
Hand_Detection_Confidence = 0.1
Hand_Tracking_Confidence = 0.1

class GestureInputScreen:
    def __init__(self, callback):
        self.btn_action_cb = callback
        self.cap = cv2.VideoCapture(0)  # 開啟預設攝影機
        if not self.cap.isOpened():
            print("無法開啟攝影機，請檢查設備。")
            self.cap = None

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode = False, max_num_hands = 2,
            min_detection_confidence = Hand_Detection_Confidence, min_tracking_confidence = Hand_Tracking_Confidence
        )
        self.drawing_utils = mp.solutions.drawing_utils
        
        # storing raw hand landmark data
        self.cur_gesture_data = []
        
        self.gesture_names = [
            "子",
            "丑",
            "寅",
            "卯",
            "辰",
            "巳",
            "午",
            "未",
            "申",
            "酉",
            "戌",
            "亥",
        ]
        self.current_gesture_index = 0
        self.assets_dir = "assets/images"

    def draw(self, frame):
        """使用 OpenCV 繪製 UI"""
        frame.fill(0)
        frame[:] = (50, 50, 50)  # 全畫面填充灰色
        # 左右分隔線
        cv2.line(frame, (700, 0), (700, WINDOW_SIZE[1]), (200, 200, 200), 2)
        # 在畫面上方顯示進度
        progress_text = f"{self.current_gesture_index + 1}/{len(self.gesture_names)} {self.gesture_names[self.current_gesture_index]}"
        cv2.putText(
            frame,
            progress_text,
            (50, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        # 左側: 攝影機畫面
        success, image = self.cap.read()
        if success:
            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_image)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.drawing_utils.draw_landmarks(
                        image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )

            image = cv2.resize(image, (640, 480))
            frame[50:530, 50:690] = image

        # 右側: 示意圖
        gesture_img_path = os.path.join(
            self.assets_dir, f"gesture_{self.current_gesture_index + 1}.jpg"
        )
        if os.path.exists(gesture_img_path):
            gesture_img = cv2.imread(gesture_img_path)
            if gesture_img is not None:
                gesture_img = cv2.resize(gesture_img, (320, 320))
                frame[100:420, 750:1070] = gesture_img

        # 按鈕區域
        self._draw_buttons(frame)

    def _draw_buttons(self, frame):
        """繪製按鈕"""
        confirm_button_x, confirm_button_y = 500, 600
        back_button_x, back_button_y = 200, 600

        cv2.rectangle(
            frame,
            (confirm_button_x, confirm_button_y),
            (confirm_button_x + 200, confirm_button_y + 50),
            (0, 255, 0),
            -1,
        )
        cv2.putText(
            frame,
            "Confirm",
            (confirm_button_x + 40, confirm_button_y + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        cv2.rectangle(
            frame,
            (back_button_x, back_button_y),
            (back_button_x + 200, back_button_y + 50),
            (0, 0, 255),
            -1,
        )
        cv2.putText(
            frame,
            "Back",
            (back_button_x + 70, back_button_y + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

    def handle_click(self, x, y):
        """處理點擊事件"""
        confirm_button_x, confirm_button_y = 500, 600
        back_button_x, back_button_y = 200, 600

        if (
            confirm_button_x <= x <= confirm_button_x + 200
            and confirm_button_y <= y <= confirm_button_y + 50
        ):
            self._save_gesture_to_GM()
            if self.current_gesture_index < len(self.gesture_names) - 1:
                self.current_gesture_index += 1
            else:
                self.btn_action_cb("home")

        if (
            back_button_x <= x <= back_button_x + 200
            and back_button_y <= y <= back_button_y + 50
        ):
            self.btn_action_cb("back")

    # This method is to save the current gesture's landmark(lm) distance to gameManager(GM)
    def _save_gesture_to_GM(self):
        # Save Raw Hands landmarks first
        success, image = self.cap.read()
        
        if success:
            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_image)
            
            right_hand_raw = []
            left_hand_raw = []

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks, results.multi_handedness
                ):
                    landmarks = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
                    hand_label = handedness.classification[0].label  # "Left" 或 "Right"
                    
                    if hand_label == "Right":
                        right_hand_raw = landmarks
                    elif hand_label == "Left":
                        left_hand_raw = landmarks
                        

                # 儲存資料至檔案
                # os.makedirs("assets", exist_ok=True)
                # file_path = os.path.join("assets", "gesture_data.json")
                # with open(file_path, "w") as f:
                #     json.dump(self.gesture_data, f, indent=4)
                
                self.cur_gesture_data = {
                    "gesture_id": self.current_gesture_index,
                    "gesture_name": self.gesture_names[self.current_gesture_index],
                    "right_hand_lm": right_hand_raw,
                    "left_hand_lm": left_hand_raw
                }
                
            # now we have the input gesture lm, we want to pass the result to GM
            self.btn_action_cb("get_gesture_input")
    
    # This Public method is to pass the result of calculated distance of lms to GM
    def get_cur_input_gesture(self):
        # Goal is to get all lm's distance from (ID = 0)'s lm (the palm)
        # from MediaPipe the lm for palm is the first point in our raw data
        
        # Right Hand:
        base_point_right = np.array(self.cur_gesture_data["right_hand_lm"][0])
        distance_right = []
        
        for i, point in enumerate(self.cur_gesture_data["right_hand_lm"]):
            if i != 0:
                distance_right.append(np.linalg.norm(np.array(point) - base_point_right))
                
        # Left Hand:
        base_point_left = np.array(self.cur_gesture_data["left_hand_lm"][0])
        distance_left = []
        
        for i, point in enumerate(self.cur_gesture_data["left_hand_lm"]):
            if i != 0:
                distance_left.append(np.linalg.norm(np.array(point) - base_point_left))
        
        # d stand for distance        
        result = {
            "gesture_id": self.current_gesture_index,
            "gesture_name": self.gesture_names[self.current_gesture_index],
            "right_hand_d": distance_right,
            "left_hand_d": distance_left
        }
        
        return result