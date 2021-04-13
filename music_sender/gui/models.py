"""Music Sender models module."""

import re
import socketserver

from ..scripts import client, server


class MusicSenderServerModel:
    """Executes music sender server operations, like --automatic, --copy"""

    HOST_PATTERN = r"192.168.\d{1,3}.\d{1,3}"
    PORT_PATTERN = r"\d+"

    def __init__(self, address):
        self.__address = address
        self.__sock_server = socketserver.ThreadingTCPServer(self.__address, 
                                                             server.DataHandler)

    def get_address(self):
        """Return the address of this server model."""
        return self.__address

    def set_address(self, address):
        """Set a new address for this server. Return True when it sucessfully
        set, otherwise, False.
        """
        host = address[0]
        port = address[1]
        hs_matched = re.match(self.HOST_PATTERN, host)
        p_matched = re.match(self.PORT_PATTERN, port)
        if hs_matched and p_matched:
            # Check Host first
            host_tokens = host.split(".")
            for token in host_tokens[2:]:
                if not 0 <= int(token) <= 255:
                    return False
            # Check port
            if not 1024 <= int(port) <= 65432:
                return False
            self.__address = address
            self.__sock_server = socketserver.ThreadingTCPServer(
                self.__address, server.DataHandler
            )
            return True
        return False

    def start_server(self, local):
        """Starts the server."""
        server.set_ambient(local)
        server.start(self.__sock_server)

    def stop_server(self):
        server.stop(self.__sock_server)
