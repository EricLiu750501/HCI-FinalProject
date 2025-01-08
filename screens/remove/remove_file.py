from utils.rm_files import *
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, FONT
from utils.CvDrawText import CvDrawText
from utils.drawing import draw_button
import cv2

class  RemoveFileScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.font_path = FONT
        self.title = "Remove File"
        self.button_titles = ["Reset Created Gestures", "Reset Created Jutsu", "Remove Temp Naruto Gestures"]
        self.rm_button_functions = [reset_created_gestures, reset_created_jutsu, remove_temp_naruto_gestures]
        self.rm_button_areas = []
        self.icon = "assets/icons/edit.png"
        self.selected_index = 0


    def draw(self, frame):
        # Draw buttons
        back_x, back_y = 950, WINDOW_SIZE[1] - 100
        cv2.rectangle(
            frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        )
        CvDrawText.puttext(
            frame,
            "返回",
            (back_x + 70, back_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        self.button_areas.append((back_x, back_y, back_x + 200, back_y + 50, "back"))

        back_x, back_y = 450, 200
        gap_y = 100
        # Draw button2
        for buttons_name in self.button_titles:
            cv2.rectangle(
                frame, (back_x, back_y), (back_x + 500, back_y + 50), (0, 255, 255), -1
            )
            CvDrawText.puttext(
                frame,
                buttons_name,
                (back_x + 70, back_y + 10),
                self.font_path,
                30,
                (0,0,0),
            )
            self.button_areas.append((back_x, back_y, back_x + 500, back_y + 50, buttons_name))
            back_y += gap_y



    def handle_click(self, x, y):
        for x1, y1, x2, y2, action in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                if action == "back":
                    self.callback("back")
                else:
                    for button_name, button_function in zip(self.button_titles, self.button_functions):
                        if action == button_name:
                            button_function()
                            break
                break