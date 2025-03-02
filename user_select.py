import tkinter as tk
import platform
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class BoundingBox:
    x_min: int
    y_min: int
    x_max: int
    y_max: int

class UserSelect(ABC):
    @abstractmethod
    def get_bounding_box(self) -> BoundingBox:
        pass

class UserSelectUbuntu(UserSelect):
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Capture")

        # Fetch screen resolution dynamically
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Make the window full screen, no borders, and transparent
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.wait_visibility(self.root)  # Wait for window to be visible
        self.root.attributes("-alpha", 0.2)  # Set transparency level
        self.root.attributes("-topmost", True)  # Ensure the window stays on top
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")  # Set window size to screen size
        
        # Create a canvas for drawing the selection box
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variables to track the rectangle coordinates
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        # Variables for the final selected window coordinates
        self.selected_coords = None

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)

    def _on_button_press(self, event):
        """Triggered when the user presses the mouse button."""
        self.start_x = event.x
        self.start_y = event.y

        # Draw the initial rectangle outline
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="white", width=2
        )

    def _on_mouse_drag(self, event):
        """Triggered when the user drags the mouse."""
        if self.start_x and self.start_y:
            # Update the coordinates of the rectangle as the user drags
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def _on_button_release(self, event):
        """Triggered when the user releases the mouse button."""
        self.end_x = event.x
        self.end_y = event.y

        # Store the selected coordinates in the form of (x_min, y_min, x_max, y_max)
        x_min = min(self.start_x, self.end_x)
        y_min = min(self.start_y, self.end_y)
        x_max = max(self.start_x, self.end_x)
        y_max = max(self.start_y, self.end_y)
        
        # Store the coordinates for returning after mainloop finishes
        self.bounding_box = BoundingBox(x_min, y_min, x_max, y_max)
        
        # Terminate the program after the selection is made
        self.root.quit()

    def get_bounding_box(self) -> BoundingBox:
        """Returns the selected coordinates after the mainloop finishes."""
        return self.bounding_box

def UserSelect() -> BoundingBox:
    # Initialize Tkinter root window
    root = tk.Tk()

    # Create and start the application
    match platform.system():
        case "Linux":
            app = UserSelectUbuntu(root)
        case _:
            raise NotImplementedError("This platform is not supported yet.")

    # Start the Tkinter main loop
    root.mainloop()

    bounding_box = app.get_bounding_box()

    root.destroy()  # Destroy the root window after mainloop finishes

    return bounding_box

if __name__ == "__main__":
    bounding_box = UserSelect()
    print(bounding_box)