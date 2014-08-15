# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TCPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
from errno import *
## NOC modules
from noc.lib.nbsocket.tcpsocket import TCPSocket


class AcceptedTCPSocket(TCPSocket):
    """
    A socket wrapping accepted TCP connection. Usually spawned by
    ListenTCP socket.
    Following methods can be overrided for desired behavior:

    * check_access(cls, address) - called before object creation
    * on_connect(self)   - called when socket connected (just after creation)
    * on_close(self)     - called when socket closed. Last method called
    * on_read(self,data) - called when new portion of data available when protocol=None or when new PDU available

    Following methods are used for operation:
    * write(self,data)   - send data (Buffered, can be delayed or split into several send)
    * close(self)        - close socket (Also implies on_close(self) event)
    """
    def __init__(self, factory, socket):
        super(AcceptedTCPSocket, self).__init__(factory, socket)
        self.handle_connect()

    @classmethod
    def check_access(cls, address):
        """
        Check connection is allowed from address
        """
        return True

    def handle_read(self):
        """
        Process incoming data
        """
        if self.socket is None:
            self.close()
            return
        try:
            data = self.socket.recv(self.READ_CHUNK)
        except socket.error, why:
            if why[0] in (ECONNRESET, ENOTCONN, ESHUTDOWN):
                self.close()
                return
            if why[0] in (EINTR, EAGAIN):
                return
            raise socket.error, why
        if data == "":
            self.close()
            return
        self.update_status()
        if self.protocol_class:
            self.protocol.feed(data)
        else:
            self.on_read(data)
