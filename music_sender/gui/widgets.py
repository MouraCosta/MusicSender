import random
import re
import socket
import socketserver
import tkinter as tk
from os import chdir
from threading import Thread
from tkinter import ttk

from ..scripts import client, server


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
    
    def label_config(self, **kwargs):
        """Make changes on the label widget."""
        self.label.config(**kwargs)
    
    def entry_config(self, **kwargs):
        """Make changes on the entry widget."""
        self.entry.config(**kwargs)


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


class HostPortForm(ttk.Frame):
    """A class that ask for a host and a port."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.host_input = LabelInput(self, "Host: ")
        self.port_input = LabelInput(self, "Port: ")
        self.host_input.grid(row=0)
        self.port_input.grid(row=1)

    def get(self):
        """Returns a tuple of strings with the host and port."""
        if self.host_input.get() and self.port_input.get():
            return self.host_input.get(), self.port_input.get()
        else:
            return (socket.gethostbyname(socket.gethostname()), 
                random.randrange(1024, 65432))

    def set(self, host, port):
        self.host_input.set(host)
        self.port_input.set(port)

    def _is_valid(self):
        """Checks if the the host and port are valid. Returns True if all is 
        valid, False if any of is invalid."""
        host, port = self.get()
        local_match = bool(re.fullmatch("127.\d{1,3}.\d{1,3}.\d{1,3}", host))
        ip_match = bool(re.fullmatch("192.168.\d{1,3}.\d{1,3}", host))
        if not ((local_match or ip_match) and (1024 < int(port) < 65432)):
            return False
        return True


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
        self.host_port_input = HostPortForm(self)

        # Widgets Setting
        self.mode_input.place(x=200, y=0)
        self.issues_table.place(x=430, y=5)
        self.host_port_input.place(x=380, y=100)
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
            return False
        else:
            print("\033[;32mDoing so fine. Path is Ok\033[m")
            return True

    def _close_mode_changer(f):
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

    @_close_mode_changer
    def _start_server(self, app_server):
        """Starts the server."""
        server.set_ambient(self.path_input.get())
        server.start(app_server)

    @_close_mode_changer
    def _click_stop_server(self, app_server):
        """Shutdown the server."""
        server.stop(app_server)

        # Sets to the initial state
        self.issues_table.set_text("")
        self.button.config(text="Start", command=self._click_server)
        self.path_input.entry.delete("0", tk.END)
        self.host_port_input.host_input.entry.delete("0", tk.END)
        self.host_port_input.port_input.entry.delete("0", tk.END)

    def _create_server(self):
        """Returns an server object. None if the the host is already 
        in use."""
        try:
            if self.host_port_input._is_valid():
                host, port = self.host_port_input.get()
                return socketserver.ThreadingTCPServer(
                (host, int(port)), server.DataHandler)
            else:
                return None
        except OSError:
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

            # Always update the form to the user see what is the address.
            self.host_port_input.set(*app_server.server_address)
            self.button.config(text="Stop", 
                command=lambda: self._click_stop_server(app_server))
        else:
            error_msg = "Error." + ("\nPath is Invalid" if not path_isvalid 
                else "\nCannot start server")
            self.issues_table.set_text(error_msg)

    @_close_mode_changer
    def _download(self, app_client, address):
        self.issues_table.set_text("WAIT !")
        client.automatic(app_client, address)
        self.issues_table.set_text("FINISHED !")

    def _click_client(self):
        """Make an automatic request to the server."""
        path_isvalid = self._validate_path()
        HOST, PORT = self.host_port_input.get()
        host_port_isvalid = self._validate_port_host_input(HOST, PORT)
        if path_isvalid and host_port_isvalid:
            app_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            success = client.set_ambient(app_client, self.path_input.get(),
                                         HOST, PORT)
            if success:
                # Creates a daemon thread for requesting the missing musics
                client_daemon = Thread(target=self._download, 
                    args=(app_client, (HOST, PORT)), daemon=True)
                client_daemon.start()
            else:
                print("\033[;31mThe client was unable to connect to the "
                      "server.\033[m")
                self.issues_table.set_text("Cannot connect to the server")
        else:
            if not path_isvalid:
                self.issues_table.set_text("Error.\nPath is invalid.")
            else:
                self.issues_table.set_text("Error.\n Host or port are invalid")
