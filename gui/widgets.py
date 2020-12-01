import tkinter as tk
from tkinter import ttk


# FIXME: Make this class more dynamic
class LabelInput(ttk.Frame):
    """A shortcut class for simulating a complete entry."""

    def __init__(self, parent, text, input_class=ttk.Entry, input_args=None,
                 input_var=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        input_args = input_args or None
        self._input_var = input_var or tk.StringVar()
        self.label = ttk.Label(self, text=text)
        self.entry = ttk.Entry(self)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.entry.grid(row=0, column=1, sticky=tk.W + tk.E)

    def get(self) -> any:
        return self._input_var.get()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("TestWindow")
    root.resizable(width=False, height=False)

    # Widgets test section
    