# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ListenUDPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
## NOC modules
from noc.lib.nbsocket.basesocket import Socket


class ListenUDPSocket(Socket):
    """
    UDP Listener. Wait for UDP packet on specified address and port
    and call .on_read() for each packet received.
    """
    CLOSE_ON_ERROR = False

    def __init__(self, factory, address, port):
        """
        :param factory: SocketFactory
        :type factory: SocketFactory
        :param address: Address to listen on
        :type address: str
        :param port: Port to listen on
        :type port: int
        """
        Socket.__init__(self, factory)
        self.address = address
        self.port = port

    def create_socket(self):
        """Create and bind socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
            self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) | 1)
        self.socket.bind((self.address, self.port))
        super(ListenUDPSocket, self).create_socket()

    def handle_read(self):
        """
        Process incoming data. Call .on_read() for each portion
        of data received
        """
        msg, transport_address = self.socket.recvfrom(self.READ_CHUNK)
        if msg == "":
            return
        self.on_read(msg, transport_address[0], transport_address[1])

    def on_read(self, data, address, port):
        """
        :param data: Data received
        :type data: str
        :param address: Source address
        :type address: str
        :param port: Source port
        :type port: int
        """
        pass

    def can_write(self):
        """
        Indicate data can be written into socket.
        """
        return False
