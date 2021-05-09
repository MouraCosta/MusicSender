"""Music Sender server script.

This script allows the user to estabilish the server for sending musics
dynamically to the client.

usage: server.py [-h] [-l LOCAL] [-hs HOST] [-p PORT]

optional arguments:
  -h, --help                  show this help message and exit
  -l LOCAL, --local LOCAL     Indicates where the script gets musics
  -hs HOST, --host HOST       Server host
  -p PORT, --port PORT        Server port

Examples:

    ms_server -hs 192.168.1.4 -p 6734 -l ~/Music/

    ms_server -hs 192.168.1.23 -p 3001
"""

import argparse
import os
import random
import re
import socket
import socketserver
import time

from . import utils


class MusicSenderServer:
    """Music Sender server.

    This is a simple TCP server that uses the IPV4 model. It's
    functionality are command-based, so as the client sends commands to
    the server, the server uses it's handler to handle all the commands
    and executes the requested operations.

    Attributes:
        HOST_PATTERN: Stores a regex pattern string for matching hosts.
        __address: A tuple that contains the server host and port.
        __local: A simple string that represents a directory path.

    Methods:
        set_ambient(): Sets the server ambient.
        start(): Starts the server.
        stop(): Shutdown and close the server.
    """

    HOST_PATTERN = r"192.168.\d{1,3}.\d{1,3}"

    def __init__(self, address: (str, int), local: str) -> None:
        """Initializes the MusicSender server.

        Args:
            address: A tuple containg a string host and a int port.
            local: The str path where the server gets musics.

        Raises:
            ValueError:
                Raised by __check_address() in case the address
                isn't valid.
        """

        self.__address = address
        self.__local = local
        MusicSenderServer.__check_address(address)
        self.__sock_server = socketserver.ThreadingTCPServer(
            address, DataHandler)

    @staticmethod
    def __check_address(address: (str, int)) -> None:
        """Checks the address.

        Since Music Sender works with IPV4 adresses only, this method
        expects to check adresses that correspond to the IPV4 model.
        For instance, the examples that follows are valid adresses.

            - ("192.168.1.4", 5000)
            - ("192.168.255.255", 8000)
            - ("192.168.1.12", 10000)

        Args:
            address:
                A tuple containing a address like
                (e.g ("localhost", 5000)).

        Raises:
            ValueError:
                Some of the address parts are incorrect or out of
                range.
        """
        matched = re.match(MusicSenderServer.HOST_PATTERN, address[0])
        if matched:
            # Check if the last two token is on range. (0 < x < 255)
            host_tokens = address[0].split(".")[2:]
            for token in host_tokens:
                if not 0 <= int(token) <= 255:
                    raise ValueError(f"Host {address[0]} out of range.")
            if not 1024 <= address[1] <= 65432:
                raise ValueError(f"Port {address[1]} out of range.")
        else:
            raise ValueError(f"Address {address} is invalid.")

    def set_ambient(self) -> bool:
        """Sets the server ambient.

        Returns:
            A boolean indicating whether the server did set the ambient
            correctly without errors or it has failed. True for success
            and False for failure.
        """

        try:
            os.chdir(self.__local)
            return True
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            return False

    def start(self) -> None:
        """Starts the server."""
        self.__sock_server.serve_forever()

    def stop(self) -> None:
        """Stops the server."""
        self.__sock_server.shutdown()
        self.__sock_server.server_close()


class DataHandler(socketserver.BaseRequestHandler):
    """A class that is responsible for receiving commands and sending
    music data binaries.

    This is a subclass of socketserver.BaseRequestHandler, so some
    commands are overriden like the handle() method. It's inner workings
    is command-based, so the main function is to execute procedures
    according to those commands.

    The following commands the class handles:

        * --copy <any integer non-negative>
        * --available
        * --diff
        * --automatic
        * --raw-available

    Methods:
        handle():
            Handle the requests. It's overriden.
        get_option():
            Function that gets an option from command sent from the
            client.
        handle_client_commands():
            Handle all the client commands.
        _send_music_file():
            Sends the music binaries to the client.
        _send_available():
            Sends the available musics to the client.
        _get_available():
            Gets the available music on the directory the server is
            working on.
    """

    def handle(self) -> None:
        print(f"\033[;33m[*] CONNECTION AT {self.client_address}\033[m")
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

    @staticmethod
    def get_option(msg) -> int:
        """Gets the requested musico ption from the client message.

        Args:
            msg: The client message command string.

        Returns:
            The option integer inside the client request message.

        Raises:
            ValueError: When the command is not valid.
        """

        msg = msg.decode()
        matches = re.match(r"--copy \d+", msg)
        if matches:
            return int(re.search(r"\d+", msg).group()) - 1
        raise ValueError("Bad command.")

    def handle_client_commands(self, msg) -> None:
        """Executes operations requested by the client.

        Args:
            msg: The client message command string.
        """
        print(f"[*] Command Received -> {msg}")
        if msg == b"--available":
            self._send_available()
        elif msg == b"--raw-available":
            self._send_available()
        elif b"--copy" in msg:
            try:
                option = DataHandler.get_option(msg)
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

    def _send_music_file(self, option: int) -> None:
        """Sends the musics binaries to the client.

        Args:
            option: The choosen music option integer.
        """
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
        """Sends all the available music on the server directory."""
        print("[*] Sending raw string available music list")
        available_musics = "|".join(DataHandler._get_available())
        if bool(available_musics):
            self.request.sendall(available_musics.encode())
            print("[*] raw string available music list sent")
            time.sleep(0.1)
            self.request.send(b"end")
        else:
            self.request.send(b"not-available")

    @staticmethod
    def _get_available() -> list:
        """Get all the available musics on the server computer."""
        return list(filter(utils.is_music_file, os.listdir(".")))


def main() -> None:
    """Main Program"""
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-l", "--local", help="Indicates where the script "
                           "gets musics", default="./", type=str)
    argparser.add_argument("-hs", "--host", help="Server host", type=str,
                           default=socket.gethostname())
    argparser.add_argument("-p", "--port", help="Server port", type=int,
                           default=random.randrange(1024, 65432))
    args = argparser.parse_args()
    server = None
    try:
        server = MusicSenderServer((args.host, args.port), args.local)
        if not server.set_ambient():
            print("Bad path string or needs root.")
            return
        print("\033[;32m[*] Server Started.\033[m")
        server.start()
    except ValueError:
        # Raised by the server.
        print("\033[;31mBad Host or port.\033[m")
    except OSError as os_error:
        # When there's another server running
        print("\033[;31mAn OS error ocurred.\033[m")
        print(os_error)
    except KeyboardInterrupt:
        # When the user want to stop the server
        server.stop()
        print("\033[;32m\nServer shut and closed.\033[m")
