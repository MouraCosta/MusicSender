import tkinter as tk
from tkinter import ttk
from widgets import *
import os


class MusicSenderApplication(tk.Tk):
    """Main program."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Window configuration
        self.title("Music Sender")
        self.geometry("600x300")

        # Widgets configuration
        self.path_input = LabelInput(self, "path")
        self.path_input.grid(row=0, column=1, sticky=tk.W)

    def _on_click(self):
        try:
            os.chdir(self.path_input.get())
        except (FileNotFoundError, PermissionError, NotADirectoryError):
            self.label_message_var.set("Not a directory")
        else:
            self.label_message_var.set(self.path_input.get())


if __name__ == "__main__":
    app = MusicSenderApplication()
    app.mainloop()
