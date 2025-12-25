# actions/mouse_controller.py
from pynput.mouse import Controller, Button

class MouseController:
    def __init__(self):
        self.mouse = Controller()

    def move_to(self, x: int, y: int):
        self.mouse.position = (x, y)

    def left_click(self):
        self.mouse.click(Button.left, 1)

    def right_click(self):
        self.mouse.click(Button.right, 1)

    def press_left(self):
        self.mouse.press(Button.left)

    def release_left(self):
        self.mouse.release(Button.left)

    def scroll(self, dy: int, dx: int = 0):
        """
        dy > 0 => scroll up
        dy < 0 => scroll down
        """
        if dy != 0 or dx != 0:
            self.mouse.scroll(dx, dy)