# screens/practice/practice_screen.py
import cv2
import numpy as np
import copy
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, FONT
from model.yolox.yolox_onnx import YoloxONNX
import csv
import random

# import speech_recognition as sr
from threading import Thread
from utils.CvDrawText import CvDrawText
import json


class PracticeScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)

        try:
            # 載入背景圖片
            self.background = cv2.imread(
                "assets/images/practice_background.png", cv2.IMREAD_COLOR
            )
            if self.background is None:
                raise FileNotFoundError("無法載入背景圖片")
            self.background = cv2.resize(self.background, WINDOW_SIZE)

            # 載入忍術列表
            self.jutsu_list = []
            with open("setting/jutsu.csv", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    chinese_name = row[0].strip()  # 中文名稱
                    english_name = row[1].strip().lower()  # 英文名稱（轉小寫方便匹配）
                    self.jutsu_list.append(
                        (chinese_name, english_name, i)
                    )  # 中文、英文、索引

            # 載入容忍詞表
            with open("setting/tolerance_terms.json", encoding="utf8") as f:
                self.tolerance_terms = json.load(f)

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
        # self.recognizer = sr.Recognizer()
        # self.microphone = sr.Microphone()

        # 新增：麥克風狀態
        self.is_recording = False
        self.is_listening = False
        self.listen_thread = None

        # 新增：識別結果顯示相關變數
        self.detected_jutsu_name = ""
        self.user_spoken_text = ""
        self.detection_timer = 0
        self.DETECTION_DISPLAY_TIME = 100  # 顯示時間（幀數）
        self.detection_status = False  # 是否成功偵測到忍術

    def _listen_for_jutsu(self):
        """持續監聽語音輸入"""
        while self.is_listening:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)

                audio = self.recognizer.listen(source, timeout=1)
                text = self.recognizer.recognize_google(audio, language="zh-TW")

                # 保存使用者說的話
                self.user_spoken_text = text
                self.detection_status = False
                normalized_text = text.replace(" ", "").lower()  # 去除空格並轉小寫
                print(f"使用者輸入: {text}")

                # 驗證是否匹配忍術（包含容忍詞表）
                for jutsu_cn, jutsu_en, jutsu_index in self.jutsu_list:
                    # 忍術名稱正規化（移除空格，轉小寫）
                    normalized_jutsu_cn = jutsu_cn.replace(" ", "").lower()
                    normalized_jutsu_en = jutsu_en.lower()

                    # 取得容忍詞表的可能詞彙
                    possible_terms = self.tolerance_terms.get(
                        jutsu_cn, [jutsu_cn]
                    )  # 預設為 [jutsu_cn]
                    normalized_possible_terms = [
                        term.replace(" ", "").lower() for term in possible_terms
                    ]

                    # 匹配條件
                    if (
                        normalized_jutsu_cn in normalized_text  # 中文忍術名稱
                        or normalized_jutsu_en in normalized_text  # 英文忍術名稱
                        or any(
                            term in normalized_text
                            for term in normalized_possible_terms
                        )  # 容忍詞表
                    ):
                        self.detected_jutsu_name = jutsu_cn
                        # 停止錄音並跳轉到 show_screen
                        self.is_recording = False
                        self.is_listening = False
                        self.callback("show_screen", jutsu_index)
                        # self.detection_status = True # (偵錯用，會直接跳到另一個螢幕不會顯示)
                        break

                # 如果沒有偵測到忍術，仍然顯示使用者說的話
                self.detection_timer = self.DETECTION_DISPLAY_TIME

    def draw(self, frame):
        self.button_areas = []

        # 使用背景圖片
        temp_frame = self.background.copy()

        # 右側顯示忍術列表
        y_offset = 100
        for jutsu_ch, jutsu_en, i in self.jutsu_list:
            CvDrawText.puttext(
                temp_frame,
                f"{jutsu_ch} ({jutsu_en})",
                (800, y_offset),
                "assets/fonts/NotoSansTC-VariableFont_wght.ttf",
                28,
                (0, 0, 0),
            )
            y_offset += 40

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
        CvDrawText.puttext(
            temp_frame,
            status_text,
            (mic_x, mic_y + 220),
            "assets/fonts/NotoSansTC-Bold.ttf",
            30,
            (0, 0, 0),
        )

        # 如果偵測到忍術或說話內容，顯示結果
        if self.detection_timer > 0:
            if self.detection_status:
                # 成功偵測到忍術(偵錯用，會直接跳到另一個螢幕不會顯示)
                detection_text = f"已偵測到: {self.detected_jutsu_name}"
                text_color = (0, 255, 0)  # 綠色文字
            else:
                # 未偵測到忍術
                detection_text = f"未知忍術: {self.user_spoken_text}"
                text_color = (0, 0, 255)  # 紅色文字

            CvDrawText.puttext(
                temp_frame,
                detection_text,
                (50, 600),
                "assets/fonts/NotoSansTC-VariableFont_wght.ttf",
                40,
                text_color,
            )
            self.detection_timer -= 1

        # 保存麥克風按鈕區域
        self.button_areas = [(mic_x, mic_y, mic_x + 200, mic_y + 200)]

        # 繪製返回按鈕 (移動到左上角)
        back_x, back_y = 50, 50
        cv2.rectangle(
            temp_frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        )
        CvDrawText.puttext(
            temp_frame,
            "返回",
            (back_x + 70, back_y + 10),
            FONT,
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
                        # 重置前的識別結果
                        self.detected_jutsu_name = ""
                        self.user_spoken_text = ""
                        self.detection_timer = 0
                        self.detection_status = False

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
