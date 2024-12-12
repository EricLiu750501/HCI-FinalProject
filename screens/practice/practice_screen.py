# screens/practice_screen.py
import cv2
import numpy as np
import copy
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE
from model.yolox.yolox_onnx import YoloxONNX
import csv
import random
import speech_recognition as sr
from threading import Thread
from utils.CvDrawText import CvDrawText


class PracticeScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)

        try:
            # 載入忍術列表
            self.jutsu_list = []
            with open("setting/jutsu.csv", encoding="utf8") as f:
                reader = csv.reader(f)
                for row in reader:
                    self.jutsu_list.append((row[0], row[1]))

            # 載入麥克風圖標
            self.mic_icon = cv2.imread(
                "assets/icons/icon_mic.png", cv2.IMREAD_UNCHANGED
            )
            if self.mic_icon is None:
                raise FileNotFoundError("無法載入麥克風圖標")
            self.mic_icon = cv2.resize(self.mic_icon, (200, 200))

        except Exception as e:
            print(f"初始化錯誤: {e}")

        # 語音識別初始化
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # 新增：麥克風狀態
        self.is_recording = False
        self.is_listening = False
        self.listen_thread = None

    def _listen_for_jutsu(self):
        """持續監聽語音輸入"""
        while self.is_listening:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = self.recognizer.listen(source, timeout=1)
                    text = self.recognizer.recognize_google(audio, language="ja-JP")

                    # 檢查是否說出了任何忍術名稱
                    for jutsu_jp, _ in self.jutsu_list:
                        if text.lower() in jutsu_jp.lower():
                            # 找到對應的jutsu ID
                            jutsu_id = self.jutsu_list.index((jutsu_jp, _))
                            self.callback("jutsu_detected", jutsu_id)
                            break
                except:
                    pass

    def draw(self, frame):
        self.button_areas = []

        # 保存原始圖像的副本
        temp_frame = frame.copy()
        temp_frame[:] = (50, 50, 50)  # 灰色背景

        # 垂直分隔線
        cv2.line(temp_frame, (700, 0), (700, WINDOW_SIZE[1]), (200, 200, 200), 2)

        # 右側顯示忍術列表
        y_offset = 100
        for jutsu_jp, jutsu_en in self.jutsu_list:
            temp_frame = CvDrawText.puttext(
                temp_frame,
                jutsu_jp,
                (750, y_offset),
                "C:/Windows/Fonts/msjh.ttc",  # 使用系統字體
                30,
                (255, 255, 255),
            )
            y_offset += 30

        # 繪製麥克風圖標（在畫面左側中間）
        mic_x = 250
        mic_y = WINDOW_SIZE[1] // 2 - 100

        # 如果正在錄音，添加紅色背景圓圈
        if self.is_recording:
            cv2.circle(temp_frame, (mic_x + 100, mic_y + 100), 120, (0, 0, 255), -1)

        # 添加麥克風圖標
        if self.mic_icon.shape[2] == 4:
            alpha = self.mic_icon[:, :, 3] / 255.0
            for c in range(3):
                temp_frame[mic_y : mic_y + 200, mic_x : mic_x + 200, c] = (
                    temp_frame[mic_y : mic_y + 200, mic_x : mic_x + 200, c]
                    * (1 - alpha)
                    + self.mic_icon[:, :, c] * alpha
                )
        else:
            temp_frame[mic_y : mic_y + 200, mic_x : mic_x + 200] = self.mic_icon

        # 添加提示文字
        status_text = "點擊開始錄音" if not self.is_recording else "點擊停止錄音"
        temp_frame = CvDrawText.puttext(
            temp_frame,
            status_text,
            (mic_x - 30, mic_y + 220),
            "C:/Windows/Fonts/msjh.ttc",  # 使用系統字體
            30,
            (255, 255, 255),
        )

        # 保存麥克風按鈕區域
        self.button_areas = [(mic_x, mic_y, mic_x + 200, mic_y + 200)]

        # 繪製返回按鈕
        back_x, back_y = 50, WINDOW_SIZE[1] - 100
        cv2.rectangle(
            temp_frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        )
        temp_frame = CvDrawText.puttext(
            temp_frame,
            "返回",
            (back_x + 70, back_y + 10),
            "C:/Windows/Fonts/msjh.ttc",  # 使用系統字體
            30,
            (255, 255, 255),
        )
        self.button_areas.append((back_x, back_y, back_x + 200, back_y + 50))

        # 將處理後的圖像複製回原始 frame
        frame[:] = temp_frame

        return frame

    def handle_click(self, x, y):
        for i, (x1, y1, x2, y2) in enumerate(self.button_areas):
            if x1 <= x <= x2 and y1 <= y <= y2:
                if i == 0:  # 麥克風按鈕
                    self.is_recording = not self.is_recording
                    if self.is_recording:
                        # 開始新的語音識別線程
                        self.is_listening = True
                        self.listen_thread = Thread(target=self._listen_for_jutsu)
                        self.listen_thread.daemon = True
                        self.listen_thread.start()
                    else:
                        # 停止語音識別
                        self.is_listening = False
                        if self.listen_thread:
                            self.listen_thread.join(timeout=1)
                elif i == 1:  # 返回按鈕
                    self.is_listening = False
                    if self.listen_thread:
                        self.listen_thread.join(timeout=1)
                    self.callback("back")
                break
