import cv2
import numpy as np
import os
import json
import time
import copy
import csv
from utils.constants import WINDOW_SIZE
from model.yolox.yolox_onnx import YoloxONNX


class GestureScreen:
    def __init__(self, callback):
        self.callback = callback

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

        # Gesture-related attributes
        self.gesture_data = []  # Store gesture data
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

        # Frame count for detection optimization
        self.frame_count = 0
        self.skip_frame = 0

    def draw(self, frame):
        """Draw UI using OpenCV"""
        frame.fill(0)
        frame[:] = (50, 50, 50)  # Fill frame with gray

        # Vertical separator line
        cv2.line(frame, (700, 0), (700, WINDOW_SIZE[1]), (200, 200, 200), 2)

        # Display progress
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

        # Left side: Camera frame
        success, image = self.cap.read()
        if success:
            image = cv2.flip(image, 1)
            debug_image = copy.deepcopy(image)

            # Object detection
            self.frame_count += 1
            if (self.frame_count % (self.skip_frame + 1)) == 0:
                bboxes, scores, class_ids = self.yolox.inference(image)

                for bbox, score, class_id in zip(bboxes, scores, class_ids):
                    class_id = int(class_id) + 1
                    if score < 0.7:
                        continue

                    # Visualization
                    x1, y1 = int(bbox[0]), int(bbox[1])
                    x2, y2 = int(bbox[2]), int(bbox[3])

                    cv2.putText(
                        debug_image,
                        f"ID:{class_id} {self.labels[class_id][0]} {score:.3f}",
                        (x1, y1 - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA,
                    )
                    cv2.rectangle(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Resize and place camera frame
            image = cv2.resize(debug_image, (640, 480))
            frame[50:530, 50:690] = image

        # Right side: Gesture reference image
        gesture_img_path = os.path.join(
            self.assets_dir, f"gesture_{self.current_gesture_index + 1}.jpg"
        )
        if os.path.exists(gesture_img_path):
            gesture_img = cv2.imread(gesture_img_path)
            if gesture_img is not None:
                gesture_img = cv2.resize(gesture_img, (320, 320))
                frame[100:420, 750:1070] = gesture_img

        # Draw buttons
        self._draw_buttons(frame)

    def _draw_buttons(self, frame):
        """Draw buttons"""
        confirm_button_x, confirm_button_y = 500, 600
        back_button_x, back_button_y = 200, 600

        # Confirm button
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

        # Back button
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
        """Handle click events"""
        confirm_button_x, confirm_button_y = 500, 600
        back_button_x, back_button_y = 200, 600

        if (
            confirm_button_x <= x <= confirm_button_x + 200
            and confirm_button_y <= y <= confirm_button_y + 50
        ):
            self._save_gesture()
            if self.current_gesture_index < len(self.gesture_names) - 1:
                self.current_gesture_index += 1
            else:
                self.callback("home")

        if (
            back_button_x <= x <= back_button_x + 200
            and back_button_y <= y <= back_button_y + 50
        ):
            self.callback("back")

    def _save_gesture(self):
        """Save gesture data"""
        success, image = self.cap.read()
        if success:
            image = cv2.flip(image, 1)

            # Detect objects
            bboxes, scores, class_ids = self.yolox.inference(image)

            # Prepare to store detected objects
            detected_objects = []

            for bbox, score, class_id in zip(bboxes, scores, class_ids):
                if score < 0.7:
                    continue

                detected_objects.append(
                    {
                        "gesture": self.gesture_names[self.current_gesture_index],
                        "class_id": int(class_id) + 1,
                        "label": self.labels[int(class_id) + 1][0],
                        "bbox": [float(x) for x in bbox],
                        "score": float(score),
                    }
                )

            # Save data to file
            os.makedirs("assets", exist_ok=True)
            file_path = os.path.join("assets", "gesture_data.json")

            # Load existing data or create new list
            try:
                with open(file_path, "r") as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []

            # Append new data
            existing_data.extend(detected_objects)

            # Save updated data
            with open(file_path, "w") as f:
                json.dump(existing_data, f, indent=4)
