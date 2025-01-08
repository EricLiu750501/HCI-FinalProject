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
        self.button_functions = [remove_gestures, remove_jutsu, remove_temp]
        self.button_areas = []
        self.icon = "assets/icons/edit.png"
        self.selected_index = 0

        self.button_width = 250
        self.button_height = 100
        self.gap = 15
        self.total_height = self.button_height 

        self.start_y = (WINDOW_SIZE[1] - self.total_height) // 2
        self.x = WINDOW_SIZE[0] // 2
        for i, button_name in enumerate(self.button_titles):
            y1 = self.start_y + i * (self.button_height + self.gap)
            x1 = self.x

            y2 = y1 + self.button_height
            x2 = x1 + self.button_width
            self.button_areas.append((x1, y1, x2, y2, button_name))



    def draw(self, frame):
        

        
        for i, button_name in enumerate(self.button_titles):
            y1 = self.start_y + i * (self.button_height + self.gap)
            x1 = self.x
            hover = i
            draw_button(
                frame,
                button_name,
                "assets/icons/icon_trash_bin.png",
                (x1, y1),
                (self.button_width, self.button_height),
                selected=False,
                hover=hover,
            )
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