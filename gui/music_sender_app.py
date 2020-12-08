import tkinter as tk
from tkinter import ttk
try:
    from . import widgets
except ImportError:
    # Since everyone use "python file.py" instead of "python -m file" 
    # this is enough
    import widgets


class MusicSenderApplication(tk.Tk):
    """Main program."""

    WINDOW_HEIGHT = 150
    WINDOW_WIDTH = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window configuration
        self.title("Music Sender")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        style = ttk.Style(self)
        style.theme_use("clam")

        widgets.MusicSenderAppForm(self).pack()


if __name__ == "__main__":
    app = MusicSenderApplication()
    app.mainloop()
