#! /usr/local/bin/python3.9
"""This is TCP client. His function is to request music binary data to the TCP
server."""

import argparse
import os
import socket
import time


def available(client):
    """Get the available music catalog in the server."""
    client.send(b"--raw-available")
    server_musics = client.recv(4096).decode("utf8")
    server_musics = server_musics.split("|")
    for i, msc in enumerate(server_musics):
        print(f"{i} -> {msc}")


def copy(client, option):
    """Get a music copy from the server."""
    command = f"--copy {option}"
    client.send(command.encode("utf8"))
    music_name = client.recv(4096)
    with open(music_name, "wb") as music_file:
        music_data = client.recv(4096)
        while music_data != b"end":
            music_file.write(music_data)
            music_data = client.recv(4096)
    print("Music file created sucessfully")


def diff(client):
    """Yields the relative index and the file name of the missing music 
    files in client."""
    client.send(b"--raw-available")
    server_mscs = client.recv(4096).decode("utf8")
    server_mscs = server_mscs.split("|")
    client_mscs = os.listdir(".")
    client_mscs = [file for file in client_mscs if file.endswith("mp3")]
    missing_client_mscs = list(
        set(server_mscs).difference(set(client_mscs)))
    for missing in missing_client_mscs:
        relative_index = server_mscs.index(missing) + 1
        yield relative_index, missing


def automatic(client):
    """Make an update in your music catalog."""
    for index, missing in diff(client):
        print(f"Creating {missing} file")
        copy(client, index)
        time.sleep(0.2)


def handle_args(client, args):
    """This function is responsible by handling the arguments."""
    if args.available and not args.diff:
        available(client)
    elif (option := args.copy):
        copy(client, option)
    elif args.automatic and not args.diff:
        automatic(client)
    elif args.diff:
        for i, mssng in diff(client):
            print(f"{i} -> {mssng}")


def set_ambient(client, args):
    """Try to connect to the server, it automatically exits when no 
    server was available."""
    try:
        client.connect(("localhost", 5000))
    except ConnectionRefusedError:
        print("\033[;31mIt was not possible to connect to the server\033[m")
        exit(1)
    try:
        os.chdir(args.local)
    except (NotADirectoryError, PermissionError, FileNotFoundError):
        print("An error has ocurred")
        print("Possible issues:\n\t-You're not root\n\t-Directory "
              "not found or its not a directory")
        exit(1)


def add_arguments(parser):
    """Add the arguments for the client applet."""
    parser.add_argument("-v", "--available", help="returns the available "
                        "music catalog", action="store_true")
    parser.add_argument("-c", "--copy", help="request a copy from a given \n"
                        "option, should make nothing if the option is "
                        "invalid", type=int)
    parser.add_argument("-d", "--diff", help="This returns a list of musics "
                        "that in server that not in client music directory",
                        action="store_true")
    parser.add_argument("-a", "--automatic", help="returns a list of musics "
                        "that is not in client directory",
                        action="store_true")
    parser.add_argument("-l", "--local", help="This is where the musics "
                        "will be received, default is ./", default=".", type=str)


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    set_ambient(client, args)
    handle_args(client, args)


if __name__ == "__main__":
    main()
