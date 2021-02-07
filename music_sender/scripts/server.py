"""This is a tcp server. He's responsible for sending music binary data to 
the client.

It provides a default handler for sending musics or data about them to the 
client."""

import argparse
import os
import random
import socketserver
import socket
from . import utils


class DataHandler(socketserver.BaseRequestHandler):
    """A class that is responsible for receiving commands and sending 
    music data binaries."""

    def handle(self) -> None:
        print(f"[*] CONNECTION AT {self.client_address}")
        while True:
            msg = self.request.recv(4096)
            if msg == "":
                break
            self.handle_client_commands(msg)

    def handle_client_commands(self, msg):
        """A function that stores the logical analysis."""
        print(f"[*] Command Received -> {msg}")
        if msg == b"--available":
            self._available()
        elif msg == b"--raw-available":
            self._send_available()
        elif b"--copy" in msg:
            option = msg.decode("utf8")
            option = int("".join(option.split()[1:])) - 1
            print(f"[*] Requested Option: {option}")
            self._send_music_file(int(option))

    # TODO: Fix the automatic function
    def _send_music_file(self, option):
        """Send the binary music data to the client."""
        music_name = None
        try:
            music_name = self._get_available()[option]
            self.request.send(music_name.encode("utf8"))
            music_file = open(music_name, "rb")
            print(f"[*] Sending {music_name}")
            self.request.sendfile(music_file)
            print(f"[*] {music_name} sent.")
            self.request.close()
        except IndexError:
            self.request.send(b"not-available")

    def _send_available(self):
        print("[*] Sending raw string available music list")
        available_musics = "|".join(self._get_available())
        if bool(available_musics):
            self.request.sendall(available_musics.encode("utf8"))
        else:
            self.request.send(b"not-available")

    def _get_available(self) -> list:
        """Get all the available musics on the server computer."""
        available_musics = list(filter(utils.is_music_file, os.listdir(".")))
        return available_musics


def set_ambient(local):
    """Set the ambient for the server."""
    try:
        os.chdir(local)
    except (NotADirectoryError, FileNotFoundError, PermissionError) as error:
        print("\033[;31m")
        if isinstance(error, NotADirectoryError):
            print(f"The \"--local\" argument {local} is not a directory")
        elif isinstance(error, FileNotFoundError):
            print(f"The \"--local\" argument {local} does not exist.")
        elif isinstance(error, PermissionError):
            print("You do not have enough permissions to access this directory.")
            print("you must be root")
        local = "./"
        os.chdir(local)
        print("In the current directory.")
        print("\033[m")


def start(server):
    """Starts the server to run."""
    print(f"[Started] --> {server.server_address}")
    server.serve_forever()


def stop(server):
    """Stops the server."""
    server.shutdown()
    server.server_close()


def main():
    """Main Program"""
    # Set the arguments for the server
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-l", "--local", help="Indicates where the script "
                           "have to found musics", default=".", type=str)
    argparser.add_argument("-hs", "--host", help="Server host", type=str,
                           default=socket.gethostname())
    argparser.add_argument("-p", "--port", help="Server port", type=int,
                           default=random.randrange(1, 65432))
    args = argparser.parse_args()
    set_ambient(args.local)
    server = None
    try:
        server = socketserver.ThreadingTCPServer((args.host, args.port),
                                                 DataHandler)
        start(server)
    except OSError:
        # When there's another server running
        print("\033[;31mThere's another server running\033[m")
    except KeyboardInterrupt:
        # When the user want to stop the server
        print("Done")
        stop(server)


if __name__ == "__main__":
    main()
