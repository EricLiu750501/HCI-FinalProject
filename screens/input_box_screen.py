import sys
import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog

from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE
from utils.CvDrawText import CvDrawText


class InputBoxScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.font_path = "assets/fonts/NotoSansTC-VariableFont_wght.ttf"
        self.button_areas = []
        self.frame = None
        
        # 初始化 Tkinter root window
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主窗口

    def draw(self, frame):
        # 保存原始圖像的副本
        temp_frame = frame.copy()
        temp_frame[:] = (50, 50, 50)  # 深灰色背景
        # 添加標題
        CvDrawText.puttext(
            temp_frame,
            f"簡易 input box 範本",
            (100, 100),
            self.font_path,
            48,
            color=(255, 255, 255),
        )
        
        # draw demo button
        back_x, back_y = 550, WINDOW_SIZE[1] - 100
        cv2.rectangle(
            temp_frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        )
        CvDrawText.puttext(
            temp_frame,
            "Demo",
            (back_x + 70, back_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        
        self.button_areas.append((back_x, back_y, back_x + 200, back_y + 50))
        
        # 繪製返回按鈕
        back_x, back_y = 50, WINDOW_SIZE[1] - 100
        cv2.rectangle(
            temp_frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        )
        CvDrawText.puttext(
            temp_frame,
            "返回",
            (back_x + 70, back_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        
        self.button_areas.append((back_x, back_y, back_x + 200, back_y + 50))
        # 將處理後的圖像複製回原始 frame
        frame[:] = temp_frame
        self.frame = frame

    def handle_click(self, x, y):
        for i, (x1, y1, x2, y2) in enumerate(self.button_areas):
            if x1 <= x <= x2 and y1 <= y <= y2:
                if i == 0:
                    user_input = self.__get_user_input()
                    self.frame = cv2.resize(self.frame, WINDOW_SIZE)
                    if user_input:
                        print(f"User Input: {user_input}")
                    break
                else:
                    self.callback("back")
                    break
            
    # Private method here ------------------------
    def __get_user_input(self):
        # use tkinter
        result = simpledialog.askstring("Title", "the message u want to pass to screen")
        if result:  # Check if the user clicked "OK"
            return result
        return None
    