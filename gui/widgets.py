import socket
import socketserver
import sys
import tkinter as tk
from os import chdir
from threading import Thread
from tkinter import ttk

#! Search for another way to import without errors. this is not beautiful
sys.path.append("./")
sys.path.append("../")

from music_sender import client, server


class LabelInput(ttk.Frame):
    """A class responsible for getting user input."""

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
        """Get the current value on the linked variable."""
        return self.input_var.get()

    def set(self, value):
        """Set a new value to the linked variable."""
        self.input_var.set(value)


class ModeSelector(ttk.Frame):
    """This class is basically two radio buttons."""

    def __init__(self, parent, option1, option2, command1, command2,
                 variable, **kwargs):
        super().__init__(parent, **kwargs)
        self.option1_radiobutton = ttk.Radiobutton(
            self, text=option1, value=option1, variable=variable,
            command=command1)
        self.option2_radiobutton = ttk.Radiobutton(
            self, text=option2, value=option2, variable=variable,
            command=command2)
        self.option1_radiobutton.grid(row=0, column=0)
        self.option2_radiobutton.grid(row=0, column=1)


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
        self.button = ttk.Button(self, text="Update",
                                 command=self._click_client)

        def client_command(): return self.button.config(
            command=self._click_client, text="Update")

        def server_command(): return self.button.config(
            command=self._click_server, text="Start")

        self.mode_input = LabelInput(self, "MODE:", ModeSelector,
            {"option1": "Server", "option2": "Client",
             "command1": server_command, "command2": client_command})

        # Set the default mode for the mode selector
        self.mode_input.set("Client")

        self.path_input = LabelInput(self, "path:", input_args={"width": 40})
        self.issues_table = StatusTable(self)

        # Widgets Setting
        self.mode_input.place(x=200, y=0)
        self.issues_table.place(x=430, y=30)
        self.path_input.place(x=4, y=52)
        self.button.place(x=230, y=110)

    def _validate_path(self):
        """Make a check to see if the path is valid. Returns True if the path 
        is acceptable, otherwise False."""
        try:
            chdir(self.path_input.get())
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            # At this point the code must interate with the status table.
            print("\033[;31mThere's an error\033[m")
            self.issues_table.set_text("Error!")
            return False
        else:
            print("\033[;32mDoing so fine. Path is Ok\033[m")
            self.issues_table.set_text("Ok")
            return True

    def _button_decorator(f):
        """Guarantees that the user do not interrupt the
        process."""

        def wrapper(self, *args, **kwargs):
            """Make an action only if when the mode selector is 
            unreachable."""
            self.mode_input.entry.option1_radiobutton.config(state=tk.DISABLED)
            self.mode_input.entry.option2_radiobutton.config(state=tk.DISABLED)
            f(self, *args, **kwargs)
            self.mode_input.entry.option1_radiobutton.config(state=tk.ACTIVE)
            self.mode_input.entry.option2_radiobutton.config(state=tk.ACTIVE)
        return wrapper

    @_button_decorator
    def _start_server(self, app_server):
        """Starts the server."""
        server.set_ambient(self.path_input.get())
        server.start(app_server)

    @_button_decorator
    def _click_stop_server(self, app_server):
        """Shutdown the server."""
        server.stop(app_server)

        # Sets to the initial state
        self.issues_table.set_text("")
        self.button.config(text="Start", command=self._click_server)
        self.path_input.entry.delete("0", tk.END)

    def _create_server(self):
        """Returns an server object. None if the the host is already 
        in use."""
        try:
            return socketserver.ThreadingTCPServer(
                ("localhost", 5000), server.DataHandler)
        except OSError:
            self.issues_table.set_text("Error")
            return None

    def _click_server(self):
        """Estabilish a server with a given directory path."""
        path_isvalid = self._validate_path()
        app_server = self._create_server()
        if path_isvalid and app_server is not None:
            # Creates a server daemon for sending musics to the client.
            server_daemon = Thread(target=self._start_server, daemon=True, 
                args=(app_server, ))
            server_daemon.start()
            self.issues_table.set_text("Server Started")
            self.button.config(text="Stop", 
                command=lambda: self._click_stop_server(app_server))
        else:
            self.issues_table.set_text("Error")

    @_button_decorator
    def _download(self, app_client):
        self.issues_table.set_text("WAIT !")
        client.automatic(app_client)
        self.issues_table.set_text("FINISHED !")
    
    def _click_client(self):
        """Make an automatic request to the server."""
        path_isvalid = self._validate_path()
        if path_isvalid:
            app_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            success = client.set_ambient(app_client, self.path_input.get())
            if success:
                # Creates a daemon thread for requesting the missing musics
                client_daemon = Thread(target=self._download, 
                    args=(app_client, ), daemon=True)
                client_daemon.start()
            else:
                print("\033[;31mThe client was unable to connect to the "
                      "server.\033[m")
                self.issues_table.set_text("ERROR !")
