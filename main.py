# main.py
import cv2
import numpy as np
import pygame
from screens.home_screen import HomeScreen
# from screens.gesture_screen import GestureScreen
from screens.practice.practice_screen import PracticeScreen
from screens.gesture_model_screen import GestureScreen
from screens.add.add_gesture_screen import AddGestureScreen
from screens.check.check_gesture_screen import CheckGestureScreen
from screens.edit.edit_screen import EditScreen
from utils.constants import WINDOW_SIZE


class GameManager:
    def __init__(self):
        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound("assets/sounds/click.wav")

        # Initialize window
        self.window_name = "Game"
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)

        # Load background
        self.background = cv2.imread("assets/images/background.jpg")
        self.background = cv2.resize(self.background, WINDOW_SIZE)

        # Initialize screens
        self.home_screen = HomeScreen(self._handle_button_click)
        self.add_gesture_screen = AddGestureScreen(self._handle_button_click)
        self.check_gesture_screen = CheckGestureScreen(self._handle_button_click)
        self.edit_screen = EditScreen(self._handle_button_click)
        
        self.gesture_screen_model = GestureScreen(self._handle_button_click)
        self.practice_screen = PracticeScreen(self._handle_button_click)
        self.current_screen = self.home_screen

        # State
        self.running = True

    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_screen.handle_click(x, y)

    def _handle_button_click(self, action, data=None):
        """Handle button clicks and screen transitions"""
        if action == "exit":
            self.running = False
        elif action == "add_gesture":
            self.current_screen = self.add_gesture_screen
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "check_gesture":
            self.current_screen = self.check_gesture_screen
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "edit":
            self.current_screen = self.edit_screen
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "gesture_screen_model":
            self.current_screen = self.gesture_screen_model
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "practice_screen":
            self.current_screen = self.practice_screen
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "back":
            self.current_screen = self.home_screen
            pygame.mixer.Sound.play(self.click_sound)

    def run(self):
        while self.running:
            # Create fresh frame from background
            frame = self.background.copy()

            # Update and draw current screen
            self.current_screen.draw(frame)

            # Display frame
            cv2.imshow(self.window_name, frame)

            # Handle keyboard input
            key = cv2.waitKey(10) & 0xFF
            if key == ord("q"):
                self.running = False

            # Check if window was closed
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                self.running = False

        cv2.destroyAllWindows()


if __name__ == "__main__":
    game = GameManager()
    game.run()
