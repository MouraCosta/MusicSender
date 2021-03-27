"""Main Program Module."""

import tkinter as tk
from tkinter import ttk

from . import widgets


class MusicSenderApplication(tk.Tk):
    """Main program."""

    WINDOW_HEIGHT = 150
    WINDOW_WIDTH = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window configuration
        self.title("Music Sender")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.resizable(False, False)
        style = ttk.Style(self)
        style.theme_use("clam")

        widgets.MusicSenderAppForm(self).pack()


def main():
    """Main Program."""
    app = MusicSenderApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
