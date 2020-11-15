#! /usr/local/bin/python3.9
"""This is TCP client. His function is to request music binary data to the TCP
server."""

import argparse
import os
import socket
import time


def available(sock):
    """Get the available music catalog in the server."""
    sock.send(b"--available")
    music_catalog = str()
    while True:
        msg = sock.recv(4096)
        if msg == b"end":
            break
        else:
            music_catalog += msg.decode("utf8")
    print(music_catalog.strip())
    print("-=" * 30)


def copy(sock, option):
    """Get a music copy from the server."""
    command = f"--copy {option}"
    sock.send(command.encode("utf8"))
    music_name = sock.recv(4096)
    with open(music_name, "wb") as music_file:
        music_data = sock.recv(4096)
        while music_data != b"end":
            music_file.write(music_data)
            music_data = sock.recv(4096)
    print("Music file created sucessfully")


def automatic(sock):
    """Make an update in your music catalog."""
    # TODO: Query the musics list from server
    sock.send(b"--raw-available")
    server_musics = sock.recv(4096).decode("utf8")
    server_musics = server_musics.split("|")

    # TODO: Query the musics from the client directory
    client_musics = os.listdir(".")
    client_musics = [file for file in client_musics if file.endswith("mp3")]

    # TODO: Get the server_musics - client_musics (I gonna use sets)
    missing_client_musics = list(
        set(server_musics).difference(set(client_musics)))

    # TODO: Request the missing_musics
    for missing in missing_client_musics:
        relative_index = server_musics.index(missing) + 1
        copy(sock, relative_index)
        time.sleep(0.2)


def handle_args(sock, args):
    """This function is responsible by handling the arguments."""
    if args.available:
        available(sock)
    elif (option := args.copy):
        copy(sock, option)
    elif args.automatic:
        automatic(sock)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--available", help="returns the available "
                        "music catalog", action="store_true")
    parser.add_argument("-c", "--copy", help="request a copy from a given \n"
                        "option, should make nothing if the option is "
                        "invalid", type=int)
    parser.add_argument("-a", "--automatic", help="returns a list of musics "
                        "that is not in client directory",
                        action="store_true")
    parser.add_argument("-l", "--local", help="This is where the musics "
                        "will be received, default is ./", default=".", type=str)
    args = parser.parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", 5000))
    except ConnectionRefusedError:
        exit(1)
    try:
        os.chdir(args.local)
    except (NotADirectoryError, PermissionError, FileNotFoundError):
        print("An error has ocurred")
        print("Possible issues:\n\t-You're not root\n\t-Directory "
              "not found or its not a directory")
        exit(1)
    handle_args(sock, args)


if __name__ == "__main__":
    main()
