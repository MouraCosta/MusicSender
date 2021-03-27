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

from . import utils


def checkout(server_data) -> None:
    """Check for error messages from the server."""
    if server_data == "not-available":
        print("There's no music on the server")
        sys.exit(0)
    elif server_data == "bad-parameter":
        print("\033[;31merror: Invalid parameter\033[m")
        sys.exit(1)


def raw_available(client) -> list:
    """Returns a list of musics."""
    client.send(b"--raw-available")
    server_musics = ""
    while True:
        music_name = client.recv(4096).decode()
        if music_name == "end":
            break
        checkout(music_name)
        server_musics += music_name
    return server_musics.split("|")


def available(client) -> None:
    """Print out the available musics on the server."""
    server_musics = raw_available(client)
    for i, msc in enumerate(server_musics):
        print(f"{i + 1} -> {msc}")


def copy(client, option) -> None:
    """Get a music copy from the server."""
    client.send(f"--copy {option}".encode("utf8"))
    music_name = client.recv(4096).decode("utf8")
    checkout(music_name)
    print(f"Creating {music_name}")
    with open(music_name, "wb") as music_file:
        client_file = client.makefile("rb")
        music_file.write(client_file.read())
        client_file.close()
    print(f"{music_name} created with success.")


def diff(client) -> (int, str):
    """Yields the relative index and the file name of the missing music
    files in client."""
    server_mscs = raw_available(client)
    client_mscs = list(filter(utils.is_music_file, os.listdir(".")))
    missing_client_mscs = list(
        set(server_mscs).difference(set(client_mscs)))
    for missing in missing_client_mscs:
        relative_index = server_mscs.index(missing) + 1
        yield relative_index, missing


def automatic(client, address) -> None:
    """Make an automatic action. It download all the remaining musics."""
    for info in diff(client):
        copy_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        copy_client.connect(address)
        copy(copy_client, info[0])


def handle_args(client, args) -> None:
    """This function is responsible by handling the arguments."""
    if args.available and not (args.diff or args.copy or args.automatic):
        available(client)
    elif args.copy and not (args.diff or args.automatic or args.available):
        option = args.copy
        copy(client, option)
    elif args.automatic and not (args.available or args.copy or args.diff):
        automatic(client, (args.host, args.port))
    elif args.diff and not (args.available or args.copy or args.automatic):
        for i, mssng in diff(client):
            print(f"{i} -> {mssng}")
    else:
        # Happens if the user try to mix options
        print("\033[;31mDon't mix options, only put the necessary\033[m")


def set_ambient(client, path, address) -> bool:
    """Try to connect to the server. Returns True when the ambient was 
    succesfully set, otherwise returns False."""
    try:
        client.connect((address[0], address[1]))
        os.chdir(path)
    except (ConnectionRefusedError, NotADirectoryError, PermissionError,
            FileNotFoundError) as err:
        if err in (FileNotFoundError, NotADirectoryError,
                   PermissionError):
            # When the error came from the chdir() or connect() functions.
            print("An error has ocurred")
            print("Possible issues:\n\t-You're not root\n\t-Directory "
                  "not found or its not a directory")
        else:
            # When it's a server error.
            print("\033[;31mIt was not possible to connect to "
                  "the server\033[m")
        return False
    return True


def add_arguments(parser) -> None:
    """Add the arguments for the client app."""
    parser.add_argument("-v", "--available", help="shows the available "
                        "music catalog and theirs code numbers",
                        action="store_true")
    parser.add_argument("-c", "--copy", help="download a music from a given "
                        "option. In case of a wrong index, a simple error "
                        "message is returned from the server", type=int)
    parser.add_argument("-d", "--diff", help="This shows a list of musics "
                        "that in server but not in client music directory. "
                        "It uses the path specified by --local.",
                        action="store_true")
    parser.add_argument("-a", "--automatic", help="downloads the list of "
                        "musics that is not in client directory.",
                        action="store_true")
    parser.add_argument("-l", "--local", help="Path where musics will be "
                        "stored. if not specified the local is the current "
                        "path.", default=".", type=str)
    parser.add_argument("-hs", "--host", help="Server host. if not specified, "
                        "the host is localhost", type=str,
                        default=socket.gethostname())
    parser.add_argument("-p", "--port", help="Server port. if not specified the"
                        " port is a range between 1024 and 65432", type=int,
                        default=random.randrange(1024, 65432))


def main() -> None:
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (args.host, args.port)
    was_succesful = set_ambient(client, args.local, address)
    if was_succesful:
        handle_args(client, args)
    else:
        client.shutdown()
        client.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
