"""This is TCP client. His function is to request music binary data to the TCP
server.

In fact, this client script contains a set of functions that are responsible 
for making some automated actions with a given client setting socket instance.
"""

import argparse
import os
import random
import socket
import sys
import time
from . import utils


def checkout(server_data):
    """Make a little check to see if the server has sent 
    not-available command."""
    if server_data == "not-available":
        print("There's no music on the server")
        sys.exit(0)


def available(client):
    """Get the available music catalog in the server."""
    client.send(b"--raw-available")
    server_musics = client.recv(4096).decode("utf8")
    checkout(server_musics)
    server_musics = server_musics.split("|")
    for i, msc in enumerate(server_musics):
        print(f"{i + 1} -> {msc}")


def copy(client, option):
    """Get a music copy from the server."""
    client.send(f"--copy {option}".encode("utf8"))
    music_name = client.recv(4096).decode("utf8")
    checkout(music_name)
    print(f"Creating {music_name}")
    with open(music_name, "wb") as music_file:
        music_file.write(client.makefile("rb").read())
    print(f"{music_name} created with success.")


def diff(client):
    """Yields the relative index and the file name of the missing music
    files in client."""
    client.send(b"--raw-available")
    server_mscs = client.recv(4096).decode("utf8")
    checkout(server_mscs)
    server_mscs = server_mscs.split("|")
    client_mscs = [file for file in os.listdir(
        ".") if utils.is_music_file(file)]
    missing_client_mscs = list(
        set(server_mscs).difference(set(client_mscs)))
    for missing in missing_client_mscs:
        relative_index = server_mscs.index(missing) + 1
        yield relative_index, missing


def automatic(client):
    """Make an update in your music catalog."""
    for info in diff(client):
        copy(client, info[0])
        time.sleep(0.2)


def handle_args(client, args):
    """This function is responsible by handling the arguments."""
    if args.available and not args.diff:
        available(client)
    elif args.copy:
        option = args.copy
        copy(client, option)
    elif args.automatic and not args.diff:
        automatic(client)
    elif args.diff:
        for i, mssng in diff(client):
            print(f"{i} -> {mssng}")


def set_ambient(client, path, host, port) -> bool:
    """Try to connect to the server, it automatically exits when no
    server was available. Returns True when the ambient was succesfully
    set, otherwise returns False."""
    try:
        client.connect((host, port))
        os.chdir(path)
    except (ConnectionRefusedError, NotADirectoryError, PermissionError,
            FileNotFoundError) as err:
        if err in (ConnectionRefusedError, NotADirectoryError,
                   PermissionError):
            # When the error came from the change_directory function
            print("An error has ocurred")
            print("Possible issues:\n\t-You're not root\n\t-Directory "
                  "not found or its not a directory")
        else:
            # When it's a server error
            print("\033[;31mIt was not possible to connect to "
                  "the server\033[m")
        return False
    return True


def add_arguments(parser):
    """Add the arguments for the client applet."""
    parser.add_argument("-v", "--available", help="shows the available "
                        "music catalog and theirs code numbers "
                        "(e.g 120, 0, 31)", action="store_true")
    parser.add_argument("-c", "--copy", help="download a music from a given "
                        "option, should make nothing if the option is "
                        "invalid", type=int)
    parser.add_argument("-d", "--diff", help="This shows a list of musics "
                        "that in server but not in client music directory "
                        "(sorry, I like math).\n This option is very useful "
                        "when you want make a single copy of a music you "
                        "don't have.",
                        action="store_true")
    parser.add_argument("-a", "--automatic", help="downloads the list of "
                        "musics that is not in client directory.",
                        action="store_true")
    parser.add_argument("-l", "--local", help="This is the path the musics "
                        "will be download, default is ./", default=".",
                        type=str)
    parser.add_argument("-hs", "--host", help="Server host", type=str,
                        default=socket.gethostname())
    parser.add_argument("-p", "--port", help="Server port", type=int,
                        default=random.randrange(1, 65432))


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    was_succesful = set_ambient(client, args.local, args.host, args.port)
    if was_succesful:
        handle_args(client, args)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
