"""This is a tcp server. He's responsible for sending music binary data to 
the client.

It provides a default handler for sending musics or data about them to the 
client."""

import argparse
import os
import random
import re
import socket
import socketserver
import time

from . import utils


class DataHandler(socketserver.BaseRequestHandler):
    """A class that is responsible for receiving commands and sending 
    music data binaries."""

    def handle(self) -> None:
        print(f"[*] CONNECTION AT {self.client_address}")
        while True:
            try:
                msg = self.request.recv(4096)
            except OSError:
                # At this point, the client has disconnected the server.
                # For now, I don't have a better solution.
                break
            if msg == b"":
                break
            self.handle_client_commands(msg)

    def get_option(self, msg) -> int:
        """Returns the option from the client request. Throws a ValueError 
        exception if the expected is not a number or is a negative number."""
        msg = msg.decode("utf8")
        matches = re.match("--copy \d+", msg)
        if (not matches):
            raise ValueError("Pattern --copy \d+ does not match with given "
                             "msg.")
        else:
            return int(re.search("\d+", msg).group()) - 1

    def handle_client_commands(self, msg) -> None:
        """A function that stores the logical analysis."""
        print(f"[*] Command Received -> {msg}")
        if msg == b"--available":
            self._available()
        elif msg == b"--raw-available":
            self._send_available()
        elif b"--copy" in msg:
            try:
                option = self.get_option(msg)
            except ValueError:
                print("\033[;31m[*] BAD CLIENT PARAMETER.\033[m")
                self.request.send(b"bad-parameter")
            else:
                print(f"[*] Requested Option: {option}")
                self._send_music_file(option)
            finally:
                # Immediately close the client
                self.request.shutdown(socket.SHUT_RDWR)
                self.request.close()

    def _send_music_file(self, option) -> None:
        """Send the binary music data to the client."""
        music_name = None
        try:
            music_name = self._get_available()[option]
            self.request.send(music_name.encode("utf8"))
            music_file = open(music_name, "rb")
            time.sleep(0.2)
            print(f"[*] Sending {music_name}")
            self.request.sendfile(music_file)
            print(f"[*] {music_name} sent.")
        except IndexError:
            self.request.send(b"not-available")

    def _send_available(self) -> None:
        """Send the raw string containing the music list."""
        print("[*] Sending raw string available music list")
        available_musics = "|".join(self._get_available())
        if bool(available_musics):
            self.request.sendall(available_musics.encode())
            print("[*] raw string available music list sent")
            time.sleep(0.1)
            self.request.send(b"end")
        else:
            self.request.send(b"not-available")

    def _get_available(self) -> list:
        """Get all the available musics on the server computer."""
        return list(filter(utils.is_music_file, os.listdir(".")))


def set_ambient(local) -> None:
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
            print("You do not have enough permissions to access this "
                  "directory.")
            print("you must be root")
        local = "./"
        os.chdir(local)
        print("In the current directory.")
        print("\033[m")


def start(server) -> None:
    """Starts the server."""
    print(f"[Started] --> {server.server_address}")
    server.serve_forever()


def stop(server) -> None:
    """Stops the server."""
    server.shutdown()
    server.server_close()


def main() -> None:
    """Main Program"""
    # Set the arguments for the server
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-l", "--local", help="Indicates where the script "
                           "gets musics", default="./", type=str)
    argparser.add_argument("-hs", "--host", help="Server host", type=str,
                           default=socket.gethostname())
    argparser.add_argument("-p", "--port", help="Server port", type=int,
                           default=random.randrange(1024, 65432))
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
