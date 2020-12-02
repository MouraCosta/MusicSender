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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window configuration
        self.title("Music Sender")
        style = ttk.Style(self)
        style.theme_use("clam")

        # Widgets configuration
        self.mode_input = widgets.LabelInput(self, "MODE:", 
            widgets.ModeSelector, {"option1": "Server", "option2": "Client"})
        self.path_input = widgets.LabelInput(self, "path:")
        self.mode_input.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.path_input.grid()


if __name__ == "__main__":
    app = MusicSenderApplication()
    app.mainloop()
