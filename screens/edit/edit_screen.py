import cv2
import json
import tkinter as tk
from tkinter import simpledialog
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, FONT
from utils.CvDrawText import CvDrawText
import csv


class EditScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.font_path = FONT
        self.current_sequence = []
        self.gestures = self._load_gestures()
        self.button_areas = []
        self.gesture_buttons = []
        self.function_buttons = []
        self.jutsu_name_zh = ""
        self.jutsu_name_en = ""
        self.is_editing_zh = False
        self.is_editing_en = False
        # 初始化 Tkinter root window
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主窗口

    def _load_gestures(self):
        gestures = []
        with open("setting/labels.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[1] != "無":
                    gestures.append({"en": row[0], "zh": row[1]})
        return gestures

    def _get_user_input(self, prompt):
        """使用 Tkinter dialog 獲取使用者輸入"""
        result = simpledialog.askstring("輸入", prompt)
        return result if result else ""

    def handle_click(self, x, y):
        # 檢查名稱輸入區域
        for bx, by, bx2, by2, action in self.button_areas:
            if bx <= x <= bx2 and by <= y <= by2:
                if action == "edit_zh":
                    self.is_editing_zh = True
                    self.is_editing_en = False
                    name = self._get_user_input("請輸入中文名稱")
                    if name:
                        self.jutsu_name_zh = name
                    return
                elif action == "edit_en":
                    self.is_editing_zh = False
                    self.is_editing_en = True
                    name = self._get_user_input("Please input English name")
                    if name:
                        self.jutsu_name_en = name
                    return

        # 檢查手勢按鈕
        for bx, by, bx2, by2, gesture in self.gesture_buttons:
            if bx <= x <= bx2 and by <= y <= by2:
                self.current_sequence.append(gesture)
                return

        # 檢查功能按鈕
        for bx, by, bx2, by2, action in self.function_buttons:
            if bx <= x <= bx2 and by <= y <= by2:
                if action == "back":
                    self.callback("back")
                elif action == "delete":
                    if self.current_sequence:
                        self.current_sequence.pop()
                elif action == "save":
                    self._save_sequence()
                break

    def _save_sequence(self):
        if (
            not self.current_sequence
            or not self.jutsu_name_zh
            or not self.jutsu_name_en
        ):
            # 使用 Tkinter messagebox 顯示錯誤訊息
            tk.messagebox.showerror("錯誤", "請確保已輸入名稱並添加手勢序列")
            return

        sequence_data = {
            "name_zh": self.jutsu_name_zh,
            "name_en": self.jutsu_name_en,
            "sequence": [g["en"] for g in self.current_sequence],
        }

        sequences = self._load_existing_sequences()
        sequences.append(sequence_data)

        with open("setting/user_jutsu.json", "w", encoding="utf-8") as f:
            json.dump(sequences, f, ensure_ascii=False, indent=2)

        # 儲存成功提示
        tk.messagebox.showinfo("成功", "序列已成功儲存")

        # 儲存後清空當前編輯的內容
        self.current_sequence = []
        self.jutsu_name_zh = ""
        self.jutsu_name_en = ""

    def _load_existing_sequences(self):
        try:
            with open("setting/user_jutsu.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def draw(self, frame):
        # 原有的 draw 方法保持不變
        self.button_areas = []
        self.gesture_buttons = []
        self.function_buttons = []

        # 白色背景
        frame[:] = (255, 255, 255)

        # 1. 顯示名稱輸入區域（最上方）
        # 中文名稱輸入框
        zh_x, zh_y = 50, 30
        cv2.rectangle(frame, (zh_x, zh_y), (zh_x + 300, zh_y + 40), (200, 200, 200), -1)
        cv2.rectangle(frame, (zh_x, zh_y), (zh_x + 300, zh_y + 40), (0, 0, 0), 1)
        name_zh_text = self.jutsu_name_zh if self.jutsu_name_zh else "點擊輸入中文名稱"
        CvDrawText.puttext(
            frame, name_zh_text, (zh_x + 10, zh_y + 8), self.font_path, 24, (0, 0, 0)
        )
        self.button_areas.append((zh_x, zh_y, zh_x + 300, zh_y + 40, "edit_zh"))

        # 英文名稱輸入框
        en_x = zh_x + 350
        cv2.rectangle(frame, (en_x, zh_y), (en_x + 300, zh_y + 40), (200, 200, 200), -1)
        cv2.rectangle(frame, (en_x, zh_y), (en_x + 300, zh_y + 40), (0, 0, 0), 1)
        name_en_text = (
            self.jutsu_name_en if self.jutsu_name_en else "Click to input English name"
        )
        CvDrawText.puttext(
            frame, name_en_text, (en_x + 10, zh_y + 8), self.font_path, 24, (0, 0, 0)
        )
        self.button_areas.append((en_x, zh_y, en_x + 300, zh_y + 40, "edit_en"))

        # 2. 顯示當前序列（上方）
        sequence_text = (
            "目前序列: " + " → ".join([g["zh"] for g in self.current_sequence])
            if self.current_sequence
            else "目前序列: (空)"
        )
        CvDrawText.puttext(
            frame, sequence_text, (50, 100), self.font_path, 36, (0, 0, 0)
        )

        # 3. 繪製手勢按鈕（中間）
        button_width = 80
        button_height = 80
        gap = 10
        start_x = 50
        start_y = 150
        per_row = 8

        for i, gesture in enumerate(self.gestures):
            row = i // per_row
            col = i % per_row
            x = start_x + col * (button_width + gap)
            y = start_y + row * (button_height + gap)

            cv2.rectangle(
                frame, (x, y), (x + button_width, y + button_height), (0, 0, 255), -1
            )
            CvDrawText.puttext(
                frame,
                gesture["zh"],
                (x + 20, y + 25),
                self.font_path,
                30,
                (255, 255, 255),
            )
            self.gesture_buttons.append(
                (x, y, x + button_width, y + button_height, gesture)
            )

        # 4. 繪製功能按鈕（下方）
        button_y = WINDOW_SIZE[1] - 150

        # 返回按鈕
        back_x = 50
        cv2.rectangle(
            frame, (back_x, button_y), (back_x + 150, button_y + 50), (0, 0, 255), -1
        )
        CvDrawText.puttext(
            frame,
            "返回",
            (back_x + 45, button_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        self.function_buttons.append(
            (back_x, button_y, back_x + 150, button_y + 50, "back")
        )

        # 刪除按鈕
        delete_x = back_x + 200
        cv2.rectangle(
            frame,
            (delete_x, button_y),
            (delete_x + 150, button_y + 50),
            (0, 0, 255),
            -1,
        )
        CvDrawText.puttext(
            frame,
            "刪除",
            (delete_x + 45, button_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        self.function_buttons.append(
            (delete_x, button_y, delete_x + 150, button_y + 50, "delete")
        )

        # 儲存按鈕
        save_x = delete_x + 200
        cv2.rectangle(
            frame, (save_x, button_y), (save_x + 150, button_y + 50), (0, 0, 255), -1
        )
        CvDrawText.puttext(
            frame,
            "儲存",
            (save_x + 45, button_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        self.function_buttons.append(
            (save_x, button_y, save_x + 150, button_y + 50, "save")
        )

        return frame
