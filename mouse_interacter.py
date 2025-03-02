import platform
import os
from abc import ABC, abstractmethod
from pynput.mouse import Controller, Button

class MouseInteracter(ABC):
    @abstractmethod
    def move(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def mouse_down(self) -> None:
        pass

    @abstractmethod
    def mouse_up(self) -> None:
        pass

class XdotoolMouseInteracter(MouseInteracter):
    def move(self, x: int, y: int) -> None:
        os.system(f"xdotool mousemove {x} {y}")

    def mouse_down(self) -> None:
        os.system("xdotool mousedown 1")

    def mouse_up(self) -> None:
        os.system("xdotool mouseup 1")

class PynputMouseInteracter(MouseInteracter):
    def __init__(self):
        self.mouse = Controller()

    def move(self, x: int, y: int) -> None:
        self.mouse.position = (x, y)

    def mouse_down(self) -> None:
        self.mouse.press(Button.left)

    def mouse_up(self) -> None:
        self.mouse.release(Button.left)

def get_mouse_interacter() -> MouseInteracter:
    match platform.system():
        case "Linux":
            return XdotoolMouseInteracter()
        case _:
            return PynputMouseInteracter()

# Example usage
if __name__ == "__main__":
    mouse = get_mouse_interacter()
    for i in range(40):
        mouse.move(100 + i, 100 + 2 * i)
