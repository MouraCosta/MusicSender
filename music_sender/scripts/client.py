"""Music Sender client.

This script allows the user to connect to the Music Sender server for
getting music through command-line. If the package isn't installed in
your system, you must run this script as a module, since imports on this
file won't work.

usage: client.py [-h] [-v] [-c COPY] [-d] [-a] [-l LOCAL] [-hs HOST]
       [-p PORT]

optional arguments:
  -h, --help            show this help message and exit.

  -v, --available       shows the available music catalog and theirs
                        code numbers.

  -c COPY, --copy COPY  download a music from a given option. In case
                        of a wrong index, a simple error message is
                        returned from the server.

  -d, --diff            This shows a list of musics that in server but
                        not in client music directory. It uses the path
                        specified by --local.

  -a, --automatic       downloads the list of musics that is not in
                        client directory.

  -l LOCAL, --local LOCAL
                        Path where musics will be stored. if not
                        specified the local is the current path.

  -hs HOST, --host HOST
                        Server host. if not specified, the host is
                        localhost.

  -p PORT, --port PORT  Server port. if not specified the port is a
                        range between 1024 and 65432
"""

import argparse
import os
import random
import re
import socket

from . import utils


class MusicSenderClient:
    """Music Sender client.

    This is a simple TCP client that use the IPV4 model. His function
    is to send commands to the server and receive the requested
    response.

    The list of command requests the client sends:

        * --copy <any integer non-negative> or
          -c <any integer non-negative>.
        * --available or -v.
        * --automatic or -a.
        * --diff or -d

    Attributes:

        address: Where the client should connect to.

        local: The path where the client will work on.

        client: A python socket that will handle low-levels calls. May
                be replaced by the automatic() method.

    Methods:

        check_address(address): Static method that checks if the given
                                address is valid.

        checkit(message): Static method that checks the server message.

        set_ambient(): Sets the ambient by changing directory and
                       connecting to the server.

        copy(option): Sends a music request to the server.

        raw_available(): Sends a request for the available musics on the
                         server and return the catalog as a list of
                         strings.

        available(): Returns a formatted string containing the music
                     catalog.

        diff(): Generates the musics name the client computer doesn't
                have.

        automatic(): Downloads all the needed musics.
    """

    HOST_PATTERN = r"192.168.\d{1,3}.\d{1,3}"

    def __init__(self, address: str, local: str) -> None:
        """Initialize the Music Sender server on a address and a path
        on the filesystem.

        Args:
            address: The host and port the client should connect to.
            local: The path where the client will work on.

        Raises:
            ValueError: When one of the arguments are invalid.
        """

        if MusicSenderClient.check_address(address):
            self.address = address
        else:
            raise ValueError("Address is not valid or parameter are not in"
                             " range")
        self.local = local
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def check_address(address: (str, int)) -> bool:
        """Checks the address.

        This checker is responsible to check if the given address is
        according to the IPV4 model. So, another type of connection
        model like IPV6, results in an error.

        Args:
            address:
                A tuple with a str and a int representing the host and
                the port respectively. Is the address to be checked.

        Returns:
            A boolean value indicating if the address is valid. True
            whether the address is valid, otherwise False.
        """

        matched = re.match(MusicSenderClient.HOST_PATTERN, address[0])
        if matched:
            # Check if the last two token is on range. (0 < x < 255)
            host_tokens = address[0].split(".")[2:]
            for token in host_tokens:
                if not 0 <= int(token) <= 255:
                    return False
            if not 1024 <= address[1] <= 65432:
                return False
        else:
            return False
        return True

    @staticmethod
    def checkit(message: str):
        """Check if the returned message is a error message from the
        server.

        Args:
            message: A string message from the server to be checked.

        Returns:
            True if the message is ok, otherwise is False.
        """

        if message in ("not-available", "bad-parameter"):
            return False
        return True

    def set_ambient(self) -> bool:
        """Sets the path where the client will work on and connects to
        the server.

        Returns:
            A boolean indicating if the ambient was sucessfully set.
            True whether the ambient was sucessfully set, otherwise
            False.
        """

        try:
            os.chdir(self.local)
            self.client.connect(self.address)
            return True
        # FIXME: This code is dangerous, not every exception should
        # pass.
        except Exception:
            # This is a bad implementation, but I don't know about audit
            # events. But False is returned whether occurs a changing
            # directory error, or a connection error.
            return False

    def copy(self, option: int) -> None:
        """Executes the --copy command.

        Args:
            option: A integer value corresponding to the music index.

        Returns:
            A string containing the created music. The string may be
            empty if the copy didn't work.
        """

        self.client.send(f"--copy {option}".encode())
        music_name = self.client.recv(4096).decode()
        if MusicSenderClient.checkit(music_name):
            with open(music_name, "wb") as music_file:
                client_file = self.client.makefile("rb")
                music_file.write(client_file.read())
                client_file.close()
        else:
            return ""
        return music_name

    def raw_available(self) -> [str]:
        """Sends a --raw-available to the server.

        Returns:
            A list of music names strings in the server.
        """

        self.client.send(b"--raw-available")
        server_musics = ""
        while True:
            music_name = self.client.recv(4096).decode()
            if music_name == "end":
                break
            MusicSenderClient.checkit(music_name)
            server_musics += music_name
        return server_musics.split("|")

    def available(self) -> str:
        """Executes the --available command.

        Returns:
            A string containing the music catalog in server.
        """

        server_musics = self.raw_available()
        music_catalog = ""
        for i, msc in enumerate(server_musics):
            music_catalog += f"{i + 1} -> {msc}\n"
        return music_catalog

    def diff(self) -> (int, str):
        """Generates all the musics the client doesn't have.

        Yields:
            A tuple containing the song relative index to the server
            musics index and his name.
        """

        server_mscs = self.raw_available()
        client_mscs = list(filter(utils.is_music_file, os.listdir(".")))
        missing_client_mscs = list(
            set(server_mscs).difference(set(client_mscs))
        )
        for missing in missing_client_mscs:
            relative_index = server_mscs.index(missing) + 1
            yield relative_index, missing

    def automatic(self) -> None:
        """Executes the --automatic command. It generates the created
        music name.

        Yields:
            A string representing the created music.
        """

        for info in self.diff():
            # FIXME: It's not efficient to create multiple sockets.
            # Implement your own socket that flushes the received data.
            copy_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            copy_client.connect(self.address)
            self.client = copy_client
            self.copy(info[0])
            self.client.close()
            yield info[1]


def handle_args(client: MusicSenderClient, args) -> None:
    """This function is responsible by handling the arguments.

    Args:

        client: A MusicSenderClient instance.
    """
    available = args.available and not (args.diff or args.copy \
                                        or args.automatic)
    copy = args.copy and not (args.diff or args.automatic or args.available)
    automatic = args.automatic and not (args.available or args.copy\
                                        or args.diff)
    diff = args.diff and not (args.available or args.copy or args.automatic)

    if available:
        catalog = client.available()
        print("               Current catalog")
        print("=" * 30)
        print(catalog)
        print("=" * 30)
    elif copy:
        option = args.copy
        created_music = client.copy(option)
        if created_music:
            print(f"\033[;32mMusic {created_music} created.\033[m")
        else:
            print("\033[;31mThe music you're looking for doesn't exist\033[m")
    elif automatic:
        print("Please wait...")
        for music_created in client.automatic():
            print(f"\033[;32m{music_created}")
        print("\033[mDone...")
    elif diff:
        for i, mssng in client.diff():
            print(f"{i} -> {mssng}")
    else:
        # Happens if the user try to mix options
        print("\033[;31mDon't mix options, only put the necessary\033[m")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the arguments for the client app.

    Args:

        parser: The ArgumentParser instance.
    """

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
    address = (args.host, args.port)
    client = None
    try:
        client = MusicSenderClient(address, args.local)
    except ValueError:
        print("\033[;31Please put only valid host adresses.\033[m")
    else:
        if client.set_ambient():
            handle_args(client, args)


if __name__ == "__main__":
    main()
