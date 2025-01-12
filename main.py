# main.py
import cv2
import numpy as np
import mediapipe as mp
import pygame
from screens.home_screen import HomeScreen

from screens.practice.practice_screen import PracticeScreen
from screens.add.add_gesture_screen import AddGestureScreen
from screens.check.check_gesture_screen import CheckGestureScreen
from screens.check.perform_jutsu_screen import PerformJutsuScreen
from screens.edit.edit_screen import EditScreen
from screens.show.show_screen import ShowScreen
from screens.remove.remove_file import RemoveFileScreen

from utils.constants import WINDOW_SIZE

import tkinter as tk


class GameManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
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
        self.practice_screen = PracticeScreen(self._handle_button_click)
        self.perform_jutsu_screen = PerformJutsuScreen(self._handle_button_click)

        self.show_screen = ShowScreen(self._handle_button_click)
        self.rm_screen = RemoveFileScreen(self._handle_button_click)
        
        self.current_screen = self.home_screen

        # State
        self.running = True

        # Detected jutsu
        self.detected_jutsu = -1

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
            self.edit_screen.load_gestures()
            self.current_screen = self.edit_screen
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "practice_screen":
            self.practice_screen.load_resources()
            self.current_screen = self.practice_screen
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "back":
            self.current_screen = self.home_screen
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "jutsu_detected":
            # 更新 detected_jutsu 為忍術編號
            self.detected_jutsu = data
            print(f"偵測到忍術: {data}")
            
            # detected a jutsu that user wants to perform
            self.current_screen = self.perform_jutsu_screen
            self.current_screen.set_jutsu(data)
        elif action == "show_screen":
            self.show_screen.set_jutsu(data)
            self.current_screen = self.show_screen
            pygame.mixer.Sound.play(self.click_sound)
        elif action == "remove_file":
            self.current_screen = self.rm_screen
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
