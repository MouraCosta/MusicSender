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


class StatusTable(ttk.Frame):
    """A table that show if there's something wrong in the app."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.label_variable = tk.StringVar()
        self.table = ttk.Labelframe(self, text="Status", labelanchor="n",
            borderwidth=1)
        self.label = ttk.Label(self.table, textvariable=self.label_variable,
            relief="flat", width=20, wraplength=160)
        self.table.grid(row=0, column=0)
        self.label.grid(row=0, column=0)
    
    def set_text(self, text):
        """Set a text indicating some error or progress."""
        self.label_variable.set(text)


class MusicSenderAppForm(ttk.Frame):
    """A dynamic form to the application."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config(width=600, height=150)
        # Widgets Creation
        self.mode_input = LabelInput(self, "MODE:", 
            ModeSelector, {"option1": "Server", "option2": "Client"})
        self.path_input = LabelInput(self, "path:", 
            input_args={"width": 40})
        self.issues_table = StatusTable(self)
        self.button = ttk.Button(self, text="Click me")

        # Widgets Setting
        self.mode_input.place(x=200, y=0)
        self.issues_table.place(x=430, y=30)
        self.path_input.place(x=4, y=52)
        self.button.place(x=230, y=110)
