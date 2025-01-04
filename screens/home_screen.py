# screens/home_screen.py
import cv2
from screens.base_screen import BaseScreen
from screens.practice.practice_screen import PracticeScreen
from utils.constants import *
from utils.drawing import draw_button
from utils.CvDrawText import CvDrawText


class HomeScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.selected_index = 0
        self.font_path = FONT
        # 中文按鈕標題
        self.button_titles = ["新增手勢", "檢查手勢", "編輯", "練習"]

        # create button areas
        self.button_areas = []

    def draw(self, frame):
        # Draw main border for button area
        # draw left bar
        right_panel_width = 200
        right_panel_x = WINDOW_SIZE[0] - right_panel_width
        cv2.rectangle(
            frame,
            (right_panel_x, 0),
            (WINDOW_SIZE[0], WINDOW_SIZE[1]),
            (100, 100, 100),
            2,
        )

        # draw top bar
        top_side_bar_height = 200
        cv2.rectangle(
            frame,
            (0, 0),
            (right_panel_x, top_side_bar_height),
            (100, 100, 100),
            2,
        )

        # Button dimensions
        button_width = 180
        button_height = 100
        gap = 15

        # Calculate starting y position for main buttons
        total_height = button_height * len(BUTTONS) + gap * (len(BUTTONS) - 1)
        start_y = (WINDOW_SIZE[1] - total_height) // 2
        x = WINDOW_SIZE[0] - button_width - 10

        # Draw main buttons
        for i, text in enumerate(BUTTONS):
            y = start_y + i * (button_height + gap)
            hover = i == self.selected_index
            draw_button(
                frame,
                text,
                ICONS[i],
                (x, y),
                (button_width, button_height),
                selected=False,
                hover=hover,
            )
            self.button_areas.append((x, y, x + button_width, y + button_height))

        # Calculate starting x position for dev buttons
        total_width = button_width * len(DEV_BUTTONS) + gap * (len(DEV_BUTTONS) - 1)
        start_x = (WINDOW_SIZE[0] - total_width) // 2
        y = 100

        # Draw develope areas buttons
        for i, text in enumerate(DEV_BUTTONS):
            x = start_x + i * (button_width + gap)
            draw_button(
                frame,
                text,
                ICONS[i],
                (x, y),
                (button_width, button_height),
                selected=False,
                hover=False,
            )
            self.button_areas.append((x, y, x + button_width, y + button_height))

        # Draw exit button
        exit_x = WINDOW_SIZE[0] - button_width - 10
        exit_y = exit_y = WINDOW_SIZE[1] - button_height // 2
        draw_button(
            frame,
            "Exit",
            "assets/icons/icon_exit.png",
            (exit_x, exit_y),
            (button_width, button_height // 2),
            selected=False,
            hover=False,
        )
        self.button_areas.append(
            (exit_x, exit_y, exit_x + button_width, exit_y + button_height // 2)
        )

    def handle_click(self, x, y):
        for i, (x1, y1, x2, y2) in enumerate(self.button_areas):
            if x1 <= x <= x2 and y1 <= y <= y2:
                if i == len(BUTTONS) + len(DEV_BUTTONS):  # Exit button
                    self.callback("exit")
                else:
                    self.selected_index = i
                    if i == 0:
                        self.callback("add_gesture")
                    elif i == 1:
                        self.callback("check_gesture")
                    elif i == 2:
                        self.callback("edit")
                    elif i == 3:
                        self.callback("practice_screen")
                    elif i == 4:
                        self.callback("gesture_screen_model")
                    elif i == 5:
                        self.callback("input_box_screen_model")
                break
