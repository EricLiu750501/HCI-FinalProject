# screens/mode_screen.py
import cv2
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, BUTTONS
from utils.drawing import draw_button

class ModeScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.mode = 0
    
    def set_mode(self, mode):
        self.mode = mode
    
    def draw(self, frame):
        self.button_areas = []
        frame[:] = (255, 255, 255)
        
        # Draw mode title
        cv2.putText(frame, f"Mode: {BUTTONS[self.mode]}", 
                   (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 
                   2, (0, 0, 0), 3)
        
        # Draw back button
        back_x, back_y = 20, 20
        draw_button(frame, "Back", "assets/icons/back_icon.png",
                   (back_x, back_y), (100, 50),
                   selected=False, hover=False)
        self.button_areas.append((back_x, back_y, 
                                back_x + 100, back_y + 50))
    
    def handle_click(self, x, y):
        for (x1, y1, x2, y2) in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.callback("back")
                break