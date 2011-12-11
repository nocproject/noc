# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UDPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
## NOC modules
from noc.lib.nbsocket.basesocket import Socket


class UDPSocket(Socket):
    """
    UDP send/receive socket
    """
    def __init__(self, factory):
        self.out_buffer = []
        super(UDPSocket, self).__init__(factory)

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super(UDPSocket, self).create_socket()

    def can_write(self):
        return bool(self.out_buffer)

    def handle_write(self):
        msg, addr = self.out_buffer.pop(0)
        self.socket.sendto(msg, addr)
        self.update_status()

    def handle_read(self):
        self.update_status()
        msg, transport_address = self.socket.recvfrom(self.READ_CHUNK)
        if msg == "":
            return
        self.on_read(msg, transport_address[0], transport_address[1])

    def on_read(self, data, address, port):
        pass

    def sendto(self, msg, addr):
        self.out_buffer += [(msg, addr)]
