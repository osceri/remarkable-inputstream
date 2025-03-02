import platform
import os
import time
from abc import ABC, abstractmethod

try:
    import ctypes
except ImportError:
    ctypes = None

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

class Win32MouseInteracter(MouseInteracter):
    def __init__(self):
        # Input structure for SendInput
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
            ]

        class INPUT(ctypes.Structure):
            _fields_ = [
                ("type", ctypes.c_ulong),
                ("mi", MOUSEINPUT)
            ]
            
        self.INPUT = INPUT
        self.MOUSEINPUT = MOUSEINPUT
        
        # Constants
        self.INPUT_MOUSE = 0
        self.MOUSEEVENTF_MOVE = 0x0001
        self.MOUSEEVENTF_ABSOLUTE = 0x8000
        self.MOUSEEVENTF_LEFTDOWN = 0x0002
        self.MOUSEEVENTF_LEFTUP = 0x0004
        
        # Load functions
        self.user32 = ctypes.windll.user32
        self.SendInput = self.user32.SendInput
        self.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
        self.SendInput.restype = ctypes.c_uint
        
        # Get screen metrics
        self.SCREEN_WIDTH = self.user32.GetSystemMetrics(0)
        self.SCREEN_HEIGHT = self.user32.GetSystemMetrics(1)
        
    def _prepare_input(self, flags, x=0, y=0):
        """Create an INPUT structure for SendInput."""

        extra = ctypes.pointer(ctypes.c_ulong(0))
        mi = self.MOUSEINPUT(x, y, 0, flags, 0, extra)
        inp = self.INPUT(self.INPUT_MOUSE, mi)
        return inp
        
    def move(self, x: int, y: int) -> None:
        # Convert to normalized coordinates (0-65535)
        norm_x = int(65535 * x // self.SCREEN_WIDTH)
        norm_y = int(65535 * y // self.SCREEN_HEIGHT)
        
        # Create input structure
        inp = self._prepare_input(
            self.MOUSEEVENTF_MOVE | self.MOUSEEVENTF_ABSOLUTE,
            norm_x, norm_y
        )
        
        # Send input
        self.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
        
    def mouse_down(self) -> None:
        inp = self._prepare_input(self.MOUSEEVENTF_LEFTDOWN)
        self.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
        
    def mouse_up(self) -> None:
        inp = self._prepare_input(self.MOUSEEVENTF_LEFTUP)
        self.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

class PynputMouseInteracter(MouseInteracter):
    def __init__(self):
        from pynput.mouse import Controller, Button
        self.mouse = Controller()
        self.Button = Button

    def move(self, x: int, y: int) -> None:
        self.mouse.position = (x, y)

    def mouse_down(self) -> None:
        self.mouse.press(self.Button.left)

    def mouse_up(self) -> None:
        self.mouse.release(self.Button.left)

def get_mouse_interacter() -> MouseInteracter:
    system = platform.system()
    
    match system:
        case "Linux":
            return XdotoolMouseInteracter()
        case "Windows":
            return Win32MouseInteracter()
        case _:
            return PynputMouseInteracter()

# Example usage
if __name__ == "__main__":
    mouse = get_mouse_interacter()
    start_time = time.time()
    
    # Move in a zigzag pattern
    for i in range(100):
        mouse.move(100 + i * 5, 100 + (i % 10) * 20)
        time.sleep(0.01)  # Small delay to see the movement
    
    # Click
    mouse.mouse_down()
    time.sleep(0.1)
    mouse.mouse_up()
    
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")