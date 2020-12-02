import tkinter as tk
from tkinter import ttk


class LabelInput(ttk.Frame):
    """A class responsible getting user input."""

    def __init__(self, parent, text, input_class=ttk.Entry, input_args=None,
                 input_var=None, **kwargs):
        super().__init__(parent, **kwargs)
        input_var = tk.StringVar() or input_var
        input_args = input_args or {}
        if input_class == ttk.Entry:
            input_args["textvariable"] = input_var
        elif input_class == ModeSelector:
            input_args["variable"] = input_var
        self.input_var = input_var
        self.label = ttk.Label(self, text=text)
        self.entry = input_class(self, **input_args)
        self.label.grid(row=0, column=0, sticky=tk.E)
        self.entry.grid(row=0, column=1, sticky=tk.W + tk.E)

    def get(self) -> any:
        return self.input_var.get()


class ModeSelector(ttk.Frame):
    """This class is basically two radio buttons."""

    def __init__(self, parent, option1, option2, variable, **kwargs):
        super().__init__(parent, **kwargs)
        option1_radiobutton = ttk.Radiobutton(
            self, text=option1, value=option1, variable=variable)
        option2_radiobutton = ttk.Radiobutton(
            self, text=option2, value=option2, variable=variable)
        option1_radiobutton.grid(row=0, column=0)
        option2_radiobutton.grid(row=0, column=1)
