import os
import platform
from abc import ABC, abstractmethod

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


def get_mouse_interacter() -> MouseInteracter:
    match platform.system():
        case "Linux":
            return XdotoolMouseInteracter()
        case _:
            raise NotImplementedError("Only Linux is supported for now")