#! /usr/local/bin/python3.9
"""This is a tcp server. He's responsible for sending music binary data to 
the client. 
It provides a default handler for sending musics or data about them to the 
client."""

import argparse
import os
import socketserver
import time

try:
    from . import utils
except ImportError:
    import utils


class DataHandler(socketserver.BaseRequestHandler):
    """A class that is responsible for receiving commands and sending 
    music data binaries."""

    def handle(self) -> None:
        print(f"[*] CONNECTION AT {self.client_address}")
        while True:
            msg = self.request.recv(4096)
            if not msg:
                break
            else:
                self.handle_client_commands(msg)

    def handle_client_commands(self, msg):
        """A function that stores the logical analysis."""
        print(f"[*] Command Received -> {msg}")
        if msg == b"--available":
            self._available()
        elif msg == b"--raw-available":
            self._raw_available()
        elif b"--copy" in msg:
            option = msg.decode("utf8")
            option = int("".join(option.split()[1:])) - 1
            print(f"[*] Requested Option: {option}")
            self._send_music_file(int(option))

    def _send_music_file(self, option):
        """Send the binary music data to the client."""
        music_name = None
        try:
            music_name = self._get_available()[option]
        except IndexError:
            self.request.send(b"not-available")
            return 0
        filename = music_name
        print(f"[*] Sending Music {filename}")
        self.request.sendall(music_name.encode("utf8"))
        time.sleep(0.2)
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    print(f"[*] Music from {filename} sent.")
                    break
                self.request.sendall(bytes_read)
            time.sleep(0.2)
            print("[*] Sending end warning to the client.")
            self.request.sendall(b"end")

    def _raw_available(self):
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
    except (NotADirectoryError, FileNotFoundError, PermissionError):
        print(f"\033[;31mThe --local arguments must be a path string, not "
              "{args.local}\033[m")
        os.chdir(".")
        print("\033[;31mSetting the path to default -> (./)\033[m")


def start(server):
    """Starts the server to run."""
    print(f"[Started] --> {('localhost', 5000)}")
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
    args = argparser.parse_args()
    set_ambient(args.local)
    server = None
    try:
        server = socketserver.ThreadingTCPServer(("localhost", 5000), 
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