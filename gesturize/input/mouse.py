"""Turns cursor position + pinch events into real OS mouse input, via pyautogui."""

import pyautogui

pyautogui.PAUSE = 0  # pyautogui's default per-call delay (0.1s) would make the cursor
                     # lag noticeably behind the hand

class MouseController:
    def __init__(self):
        self.button_down = False

    def move(self, screen_x: int, screen_y: int):
        pyautogui.moveTo(screen_x, screen_y)

    def press(self):
        if not self.button_down:
            pyautogui.mouseDown()
            self.button_down = True

    def release(self):
        if self.button_down:
            pyautogui.mouseUp()
            self.button_down = False
