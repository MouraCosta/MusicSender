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


def diff(sock):
    """Yields the relative index and the file name of the missing music 
    files in client."""
    sock.send(b"--raw-available")
    server_mscs = sock.recv(4096).decode("utf8")
    server_mscs = server_mscs.split("|")
    client_mscs = os.listdir(".")
    client_mscs = [file for file in client_mscs if file.endswith("mp3")]
    missing_client_mscs = list(
        set(server_mscs).difference(set(client_mscs)))
    message = str()
    for missing in missing_client_mscs:
        relative_index = server_mscs.index(missing) + 1
        yield relative_index, missing


def automatic(sock):
    """Make an update in your music catalog."""
    for index, missing in diff(sock):
        print(f"Creating {missing} file")
        copy(sock, index)
        time.sleep(0.2)


def handle_args(sock, args):
    """This function is responsible by handling the arguments."""
    if args.available and not args.diff:
        available(sock)
    elif (option := args.copy):
        copy(sock, option)
    elif args.automatic and not args.diff:
        automatic(sock)
    elif args.diff:
        for i, mssng in diff(sock):
            print(f"{i} -> {mssng}")


def main():
    parser = argparse.ArgumentParser()
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
