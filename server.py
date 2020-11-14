#! /usr/local/bin/python3.9
"""This is a tcp server. His function is to receive the music
name from a client and create that file in the executing machine."""

import argparse
import os
import socketserver
import time

argparser = argparse.ArgumentParser()
argparser.add_argument("-l", "--local", help="Indicates where the script "
                       "have to found musics", default="./sounds")
args = argparser.parse_args()
try:
    os.chdir(args.local)
except (NotADirectoryError, FileNotFoundError, PermissionError):
    print(f"\033[;33mThe --local arguments must be a path string, not "
          "{args.local}\033[m")
    os.chdir("./sounds")
    print("\033[;33mSetting the path to default -> (./sounds)\033[m")


class DataHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        print(f"[*] CONNECTION AT {self.client_address}")
        while True:
            msg = self.request.recv(4096)
            if not msg:
                break
            else:
                print(f"command received -> {msg}")
                if msg == b"--available":
                    self._available()
                elif msg == b"--raw-available":
                    self._raw_available()
                elif b"--copy" in msg:
                    option = msg.decode("utf8")
                    option = int("".join(option.split()[1:])) - 1
                    print(f"[*] Requested Option: {option}")
                    self._send_music_file(int(option))

    def _available(self):
        """Show the available music in the server."""
        print("[*] Sending the available music in the server")
        for pos, option in enumerate(os.listdir()):
            client_msg = f"{pos + 1} -> {option}\n"
            time.sleep(0.1)
            self.request.send(client_msg.encode("utf8"))
        self.request.sendall(b"end")
        print("[*] Available music sent")

    def _send_music_file(self, option):
        """Send the binary music data to the client."""
        music_name = os.listdir()[option]
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
        available_musics = "|".join(os.listdir())
        self.request.sendall(available_musics.encode("utf8"))


if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(("localhost", 5000), DataHandler)
    print(f"[Started] --> {('localhost', 5000)}")
    server.serve_forever()
