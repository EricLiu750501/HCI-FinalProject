import cv2
import json
import tkinter as tk
from tkinter import simpledialog
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, FONT_BOLD
from utils.CvDrawText import CvDrawText
import csv


class EditScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.font_path = FONT_BOLD
        self.current_sequence = []
        self.gestures = self.__load_gestures()
        self.current_size = len(self.__load_existing_sequences())
        self.button_areas = []
        self.gesture_buttons = []
        self.function_buttons = []
        self.jutsu_name_zh = ""
        self.jutsu_name_en = ""
        self.is_editing_zh = False
        self.is_editing_en = False

        self.COLORS = {
            "gesture_btn": (102, 140, 255),  # 溫和的橙色
            "func_btn": {
                "back": (51, 153, 255),  # 溫和橙色
                "clear": (80, 80, 245),  # 溫和紅色
                "backspace": (71, 99, 255),  # 溫和橙色
                "save": (102, 255, 80),  # 溫和綠色
            },
            "text_input": (240, 240, 240),  # 淺灰色
        }

        # 初始化 Tkinter root window
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主窗口

    def __load_gestures(self):
        gestures = []
        # 讀取 labels.csv
        with open("setting/labels.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            i = 1
            for row in reader:
                if row[1] != "無":
                    gestures.append({"en": row[0], "zh": row[1], "id": i})
                    i += 1

        # 讀取 created_gestures_d.json
        try:
            with open("setting/created_gestures_d.json", "r", encoding="utf-8") as file:
                created_gestures = json.load(file)
                for gesture in created_gestures:
                    gestures.append(
                        {
                            "en": gesture.get("g_name_en", "Unknown"),
                            "zh": gesture.get("g_name_zh", "未知"),
                            "id": gesture.get("g_id", i),
                        }
                    )
                    i += 1
        except (FileNotFoundError, json.JSONDecodeError):
            print("Warning: created_gestures_d.json not found or invalid format.")

        return gestures

    def __get_user_input(self, prompt):
        """使用 Tkinter dialog 獲取使用者輸入"""
        result = simpledialog.askstring("輸入", prompt)
        return result if result else ""

    def __clear_content(self):
        """清空當前編輯的內容"""
        self.current_sequence = []
        self.jutsu_name_zh = ""
        self.jutsu_name_en = ""

    def __save_sequence(self):
        if (
            not self.current_sequence
            or not self.jutsu_name_zh
            or not self.jutsu_name_en
        ):
            # 使用 Tkinter messagebox 顯示錯誤訊息
            tk.messagebox.showerror("錯誤", "請確保已輸入名稱並添加手勢序列")
            return

        # 載入現有的術語
        user_sequences = self.__load_existing_sequences()
        default_sequence = self.__load_default_sequences()
        total_sequence = user_sequences + default_sequence

        # 檢查是否有重複的名稱
        for seq in total_sequence:
            if seq["name_zh"] == self.jutsu_name_zh:
                tk.messagebox.showerror("錯誤", "中文名稱已存在，請選擇其他名稱")
                return
            if seq["name_en"] == self.jutsu_name_en:
                tk.messagebox.showerror("錯誤", "英文名稱已存在，請選擇其他名稱")
                return
        sequence_data = {
            "id": 6 + self.current_size + 1,
            "name_zh": self.jutsu_name_zh,
            "name_en": self.jutsu_name_en,
            "sequence": [g["id"] for g in self.current_sequence],
        }
        self.current_size += 1

        user_sequences.append(sequence_data)

        with open("setting/user_jutsu.json", "w", encoding="utf-8") as f:
            json.dump(user_sequences, f, ensure_ascii=False, indent=2)

        # 儲存成功提示
        tk.messagebox.showinfo("成功", "序列已成功儲存")

        # 儲存後清空當前編輯的內容
        self.current_sequence = []
        self.jutsu_name_zh = ""
        self.jutsu_name_en = ""

    def __load_existing_sequences(self):
        try:
            with open("setting/user_jutsu.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def __load_default_sequences(self):
        try:
            with open("setting/default_jutsu.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def handle_click(self, x, y):
        # 檢查名稱輸入區域
        for bx, by, bx2, by2, action in self.button_areas:
            if bx <= x <= bx2 and by <= y <= by2:
                if action == "edit_zh":
                    self.is_editing_zh = True
                    self.is_editing_en = False
                    name = self.__get_user_input("請輸入中文名稱")
                    if name:
                        self.jutsu_name_zh = name
                    return
                elif action == "edit_en":
                    self.is_editing_zh = False
                    self.is_editing_en = True
                    name = self.__get_user_input("Please input English name")
                    if name:
                        self.jutsu_name_en = name
                    return

        # 檢查手勢按鈕
        for bx, by, bx2, by2, gesture in self.gesture_buttons:
            if bx <= x <= bx2 and by <= y <= by2:
                if len(self.current_sequence) >= 10:
                    tk.messagebox.showwarning("警告", "最多只能輸入10個手勢！")
                    return
                self.current_sequence.append(gesture)
                return

        # 檢查功能按鈕
        for bx, by, bx2, by2, action in self.function_buttons:
            if bx <= x <= bx2 and by <= y <= by2:
                if action == "back":
                    self.__clear_content()  # 清空內容
                    self.callback("back")
                elif action == "delete":
                    if self.current_sequence:
                        self.current_sequence.pop()
                elif action == "save":
                    self.__save_sequence()
                elif action == "clear":
                    self.__clear_content()  # 呼叫清空功能
                break

    def draw(self, frame):
        self.button_areas = []
        self.gesture_buttons = []
        self.function_buttons = []

        # 載入背景圖片
        background_image = cv2.imread("assets/images/edit_background.png")
        if background_image is not None:
            # 確保背景圖片大小符合視窗大小
            background_image = cv2.resize(
                background_image, (frame.shape[1], frame.shape[0])
            )
            frame[:] = background_image
        else:
            # 如果背景圖片無法載入，使用白色背景
            frame[:] = (255, 255, 255)

        # 名稱輸入區域
        zh_x, zh_y = 50, 30
        cv2.rectangle(
            frame, (zh_x, zh_y), (zh_x + 300, zh_y + 50), self.COLORS["text_input"], -1
        )
        cv2.rectangle(frame, (zh_x, zh_y), (zh_x + 300, zh_y + 50), (0, 0, 0), 1)
        name_zh_text = self.jutsu_name_zh if self.jutsu_name_zh else "點擊輸入中文名稱"
        CvDrawText.puttext(
            frame, name_zh_text, (zh_x + 10, zh_y + 10), self.font_path, 24, (0, 0, 0)
        )
        self.button_areas.append((zh_x, zh_y, zh_x + 300, zh_y + 40, "edit_zh"))

        en_x = zh_x + 350
        cv2.rectangle(
            frame, (en_x, zh_y), (en_x + 350, zh_y + 50), self.COLORS["text_input"], -1
        )
        cv2.rectangle(frame, (en_x, zh_y), (en_x + 350, zh_y + 50), (0, 0, 0), 1)
        name_en_text = (
            self.jutsu_name_en if self.jutsu_name_en else "Click to input English name"
        )
        CvDrawText.puttext(
            frame, name_en_text, (en_x + 10, zh_y + 8), self.font_path, 24, (0, 0, 0)
        )
        self.button_areas.append((en_x, zh_y, en_x + 300, zh_y + 40, "edit_en"))

        # 顯示當前序列和Backspace按鈕
        sequence_text = (
            "目前序列: " + "→".join([g["zh"] for g in self.current_sequence])
            if self.current_sequence
            else "目前序列: (空)"
        )
        CvDrawText.puttext(
            frame, sequence_text, (50, 110), self.font_path, 36, (0, 0, 0)
        )
        # Backspace按鈕
        backspace_x = 940
        backspace_y = 110
        backspace_width = 220
        backspace_height = 60
        cv2.rectangle(
            frame,
            (backspace_x, backspace_y),
            (backspace_x + backspace_width, backspace_y + backspace_height),
            self.COLORS["func_btn"]["backspace"],
            -1,
        )
        CvDrawText.puttext(
            frame,
            "Backspace",
            (backspace_x + 25, backspace_y + 8),
            self.font_path,
            30,
            (255, 255, 255),
        )
        self.function_buttons.append(
            (
                backspace_x,
                backspace_y,
                backspace_x + backspace_width,
                backspace_y + backspace_height,
                "delete",
            )
        )

        # 手勢按鈕
        button_width = 80
        button_height = 80
        gap = 10
        start_x = 50
        start_y = 200
        per_row = 8

        for i, gesture in enumerate(self.gestures):
            row = i // per_row
            col = i % per_row
            x = start_x + col * (button_width + gap)
            y = start_y + row * (button_height + gap)

            cv2.rectangle(
                frame,
                (x, y),
                (x + button_width, y + button_height),
                self.COLORS["gesture_btn"],
                -1,
            )
            CvDrawText.puttext(
                frame,
                gesture["zh"],
                (x + 25, y + 20),
                self.font_path,
                30,
                (255, 255, 255),
            )
            self.gesture_buttons.append(
                (x, y, x + button_width, y + button_height, gesture)
            )

        # 功能按鈕
        button_y = WINDOW_SIZE[1] - 150
        func_button_width = 150
        func_button_height = 60

        # 功能按鈕配置
        buttons = [("返回", "back", 50), ("清空", "clear", 250), ("儲存", "save", 450)]

        for text, action, x_pos in buttons:
            cv2.rectangle(
                frame,
                (x_pos, button_y),
                (x_pos + func_button_width, button_y + func_button_height),
                self.COLORS["func_btn"][action],
                -1,
            )
            CvDrawText.puttext(
                frame,
                text,
                (x_pos + 45, button_y + 10),
                self.font_path,
                30,
                (255, 255, 255),
            )
            self.function_buttons.append(
                (
                    x_pos,
                    button_y,
                    x_pos + func_button_width,
                    button_y + func_button_height,
                    action,
                )
            )

        return frame
