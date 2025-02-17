# screens/practice/practice_screen.py
import cv2
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, FONT_BOLD
import json
import speech_recognition as sr
from threading import Thread
from utils.CvDrawText import CvDrawText


class PracticeScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.background = None
        self.jutsu_list = []
        self.combined_jutsu = None
        self.tolerance_terms = {}
        self.button_areas = []
        self.load_resources()  # 初始化時載入一次

        # 初始化按鈕
        self.__setup_button()

        # 載入背景圖片
        self.background = cv2.imread(
            "assets/images/practice_background.png", cv2.IMREAD_COLOR
        )
        if self.background is None:
            raise FileNotFoundError("無法載入背景圖片")
        self.background = cv2.resize(self.background, WINDOW_SIZE)

        # 載入麥克風圖標
        try:
            self.mic_icon = cv2.imread(
                "assets/icons/icon_mic.png", cv2.IMREAD_UNCHANGED
            )
            if self.mic_icon is None:
                raise FileNotFoundError("無法載入麥克風圖標")
            self.mic_icon = cv2.resize(self.mic_icon, (200, 200))
        except Exception as e:
            print(f"初始化麥克風圖標錯誤: {e}")

        # 語音識別初始化
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # 新增：麥克風狀態
        self.is_recording = False
        self.is_listening = False
        self.listen_thread = None

        # 新增：識別結果顯示相關變數
        self.detected_jutsu_name = ""
        self.user_spoken_text = ""
        self.detection_timer = 0
        self.DETECTION_DISPLAY_TIME = 30  # 顯示時間（幀數）
        self.detection_status = False  # 是否成功偵測到忍術

    def __listen_for_jutsu(self):
        """持續監聽語音輸入"""
        while self.is_listening:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)

                # listen會偵測音量並偵測聲音大的片段回傳
                audio = self.recognizer.listen(source, timeout=None)
                text = self.recognizer.recognize_google(audio, language="zh-TW")

                # 保存使用者說的話
                self.user_spoken_text = text
                self.detection_status = False
                normalized_text = text.replace(" ", "").lower()  # 去除空格並轉小寫
                print(f"使用者輸入: {text}")

                # 驗證是否匹配忍術（包含容忍詞表）
                for jutsu in self.jutsu_list:
                    normalized_jutsu_cn = jutsu["normalized_chinese_name"]
                    normalized_jutsu_en = jutsu["english_name"]

                    possible_terms = self.tolerance_terms.get(
                        normalized_jutsu_cn, [normalized_jutsu_cn]
                    )

                    if (
                        normalized_jutsu_cn in normalized_text
                        or normalized_jutsu_en in normalized_text
                        or any(term in normalized_text for term in possible_terms)
                    ):
                        self.detected_jutsu_name = jutsu["chinese_name"]
                        self.is_recording = False
                        self.is_listening = False
                        self.detection_status = True
                        self.callback(
                            "jutsu_detected", self.combined_jutsu[jutsu["index"] - 1]
                        )
                        # minus 1 because jutsu start with id = 1, but list elements start at 0

                        break
                if self.detection_status == False:
                    self.detection_timer = self.DETECTION_DISPLAY_TIME

    def __setup_button(self):
        # 保存麥克風按鈕區域
        mic_x = 250
        mic_y = WINDOW_SIZE[1] // 2 - 100
        self.button_areas.append((mic_x, mic_y, mic_x + 200, mic_y + 200))
        # 繪製返回按鈕 (移動到左上角)
        back_x, back_y = 50, 50
        self.button_areas.append((back_x, back_y, back_x + 200, back_y + 50))

    def draw(self, frame):

        # 使用背景圖片
        temp_frame = self.background.copy()

        # 右側顯示忍術列表
        y_offset = 100
        for jutsu in self.jutsu_list:
            jutsu_ch = jutsu["chinese_name"]
            jutsu_en = jutsu["english_name"]
            i = jutsu["index"]
            CvDrawText.puttext(
                temp_frame,
                f"{jutsu_ch} ({jutsu_en})",
                (800, y_offset),
                FONT_BOLD,
                28,
                (0, 0, 0),
            )
            y_offset += 50

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
            FONT_BOLD,
            30,
            (0, 0, 0),
        )

        # 如果偵測到忍術或說話內容，顯示結果
        if self.detection_timer > 0 and self.detection_status == False:
            # 未偵測到忍術
            detection_text = f"未知忍術: {self.user_spoken_text}"
            text_color = (0, 0, 255)  # 紅色文字

            CvDrawText.puttext(
                temp_frame,
                detection_text,
                (50, 150),
                FONT_BOLD,
                40,
                text_color,
            )
            self.detection_timer -= 1

        # 繪製返回按鈕 (移動到左上角)
        back_x, back_y = 50, 50
        func_button_width = 150
        func_button_height = 60
        cv2.rectangle(
            temp_frame,
            (back_x, back_y),
            (back_x + func_button_width, back_y + func_button_height),
            (40, 40, 245),
            -1,
        )
        CvDrawText.puttext(
            temp_frame,
            "返回",
            (back_x + 45, back_y + 10),
            FONT_BOLD,
            30,
            (255, 255, 255),
        )

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
                        self.listen_thread = Thread(target=self.__listen_for_jutsu)
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
                    self.is_recording = False
                    self.is_listening = False
                    self.detected_jutsu_name = ""
                    self.user_spoken_text = ""
                    self.detection_timer = 0
                    self.detection_status = False
                    self.callback("back")
                break

    def load_resources(self):
        # 載入忍術列表
        self.jutsu_list = []
        with open("setting/default_jutsu.json", encoding="utf-8") as f:
            default_jutsu = json.load(f)
        with open("setting/user_jutsu.json", encoding="utf-8") as f:
            user_jutsu = json.load(f)
        self.combined_jutsu = default_jutsu + user_jutsu
        for jutsu in self.combined_jutsu:
            chinese_name = jutsu["name_zh"].strip()
            english_name = jutsu["name_en"].strip().lower()
            normalized_chinese_name = chinese_name.replace(" ", "").lower()
            self.jutsu_list.append(
                {
                    "chinese_name": chinese_name,
                    "english_name": english_name,
                    "normalized_chinese_name": normalized_chinese_name,
                    "index": int(jutsu["id"]),
                }
            )

        # 載入容忍詞表
        with open("setting/tolerance_terms.json", encoding="utf8") as f:
            raw_tolerance_terms = json.load(f)
        self.tolerance_terms = {
            key.replace(" ", "").lower(): [
                term.replace(" ", "").lower() for term in terms
            ]
            for key, terms in raw_tolerance_terms.items()
        }
