import tkinter as tk
from tkinter import ttk
import os


class LabelInput(ttk.Frame):
    """A shortcut class for simulating a complete entry."""

    def __init__(self, parent, text="Common", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label = ttk.Label(self, text=text)
        self.entry = ttk.Entry(self)
        self.label.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)

    def get(self):
        return self.entry.get()


class MusicSenderApplication(tk.Tk):
    """Main program."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Music Sender")
        self.path_input = LabelInput(self, "path")
        self.button = ttk.Button(self, text="UPDATE", command=self.on_click)
        self.label_message_var = tk.StringVar()
        self.label_message_var.set("Click the button when you're done")
        self.label = ttk.Label(self, textvariable=self.label_message_var)
        self.path_input.grid(row=0, column=0, sticky=tk.E)
        self.button.grid(row=1, sticky=tk.E + tk.W)
        self.label.grid(row=2)

    def on_click(self):
        try:
            os.chdir(self.path_input.get())
        except (FileNotFoundError, PermissionError, NotADirectoryError):
            self.label_message_var.set("Not a directory")
        else:
            self.label_message_var.set(self.path_input.get())


if __name__ == "__main__":
    app = MusicSenderApplication()
    app.mainloop()
