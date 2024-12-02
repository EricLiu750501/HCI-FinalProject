# main.py
import cv2
import numpy as np
import pygame
from screens.home_screen import HomeScreen
from screens.mode_screen import ModeScreen
from utils.constants import WINDOW_SIZE

class GameManager:
    def __init__(self):
        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound("assets/sounds/click.wav")
        
        # Initialize window
        self.window_name = 'Game'
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
        
        # Load background
        self.background = cv2.imread("assets/images/background.jpg")
        self.background = cv2.resize(self.background, WINDOW_SIZE)
        
        # Initialize screens
        self.home_screen = HomeScreen(self._handle_button_click)
        self.mode_screen = ModeScreen(self._handle_button_click)
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
        elif action == "mode":
            self.mode_screen.set_mode(data)  # data contains the selected mode index
            self.current_screen = self.mode_screen
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
            if key == ord('q'):
                self.running = False
            
            # Check if window was closed
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                self.running = False

        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = GameManager()
    game.run()