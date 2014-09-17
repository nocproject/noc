# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UDPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
from errno import *
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
        if self.out_buffer:
            self.set_status(w=True)

    def handle_write(self):
        while self.out_buffer:
            msg, addr = self.out_buffer.pop(0)
            try:
                self.socket.sendto(msg, addr)
            except socket.error, why:  # ENETUNREACH
                self.debug("Socket error: %s" % why)
                self.close()
                return
        self.set_status(w=bool(self.out_buffer))
        self.update_status()

    def handle_read(self):
        self.update_status()
        try:
            msg, transport_address = self.socket.recvfrom(self.READ_CHUNK)
        except socket.error, why:
            if why[0] in (EINTR, EAGAIN):
                return
            raise socket.error, why
        if not msg:
            return
        self.on_read(msg, transport_address[0], transport_address[1])

    def on_read(self, data, address, port):
        pass

    def sendto(self, msg, addr):
        self.out_buffer += [(msg, addr)]
        if self.socket:
            self.set_status(w=bool(self.out_buffer))
