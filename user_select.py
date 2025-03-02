import tkinter as tk
from dataclasses import dataclass
import screeninfo
import pynput

@dataclass
class BoundingBox:
    x_min: int
    y_min: int
    x_max: int
    y_max: int

    def is_inside(self, x: int, y: int) -> bool:
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max

def get_current_screen_bounding_box() -> BoundingBox:
    controller = pynput.mouse.Controller()
    current_x, current_y = controller.position

    for screen in screeninfo.get_monitors():
        bounding_box = BoundingBox(
            x_min=screen.x,
            y_min=screen.y,
            x_max=screen.x + screen.width,
            y_max=screen.y + screen.height
        )

        if bounding_box.is_inside(current_x, current_y):
            return bounding_box

class UserSelect:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Capture")

        # Get the current active monitor position
        self.bounds = get_current_screen_bounding_box()
        
        # Make the window full screen, no borders, and transparent
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.wait_visibility(self.root)  # Wait for window to be visible
        self.root.attributes("-alpha", 0.2)  # Set transparency level
        self.root.attributes("-topmost", True)  # Ensure the window stays on top
        
        # Position window on the active monitor
        self.root.geometry(f"{self.bounds.x_max - self.bounds.x_min}x{self.bounds.y_max - self.bounds.y_min}+{self.bounds.x_min}+{self.bounds.y_min}")
        
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
        
        # Add escape key binding to quit
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def _on_button_press(self, event):
        """Triggered when the user presses the mouse button."""
        self.start_x = event.x
        self.start_y = event.y

        # Draw the initial rectangle outline
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        # White but transparent rectangle
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="white", width=2,
            stipple="gray50", fill="white"
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
        # Include the monitor offset to get screen-absolute coordinates
        x_min = min(self.start_x, self.end_x)
        y_min = min(self.start_y, self.end_y)
        x_max = max(self.start_x, self.end_x)
        y_max = max(self.start_y, self.end_y)
        
        # Store the coordinates for returning after mainloop finishes
        self.bounding_box = BoundingBox(
            x_min=self.bounds.x_min + x_min,
            y_min=self.bounds.y_min + y_min,
            x_max=self.bounds.x_min + x_max,
            y_max=self.bounds.y_min + y_max
        )
        
        # Terminate the program after the selection is made
        self.root.quit()

    def get_bounding_box(self) -> BoundingBox:
        """Returns the selected coordinates after the mainloop finishes."""
        return self.bounding_box

def user_select() -> BoundingBox:
    # Initialize Tkinter root window
    root = tk.Tk()

    app = UserSelect(root)

    # Start the Tkinter main loop
    root.mainloop()

    try:
        bounding_box = app.get_bounding_box()
    except AttributeError:
        # Handle case where user closes window without selecting
        bounding_box = None

    root.destroy()  # Destroy the root window after mainloop finishes

    return bounding_box

if __name__ == "__main__":
    bounding_box = user_select()
    print(bounding_box)