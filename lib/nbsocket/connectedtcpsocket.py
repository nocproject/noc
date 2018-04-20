# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ConnectedTCPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
from errno import *
## NOC modules
from noc.lib.nbsocket.tcpsocket import TCPSocket


class ConnectedTCPSocket(TCPSocket):
    """
    A socket wrapping connecting TCP connection.
    Following methods can be overrided for desired behavior:

    * on_connect(self)   - called when connection established and socket read to send data (first event)
    * on_close(self)     - called when socket closed. Last method called
    * on_read(self,data) - called when new portion of data available
    * on_conn_refused(self) - called when connection refused (Also implies close(self). first event)

    Following methods are used for operation:
    * write(self,data)   - send data (Buffered, can be delayed or split into several send)
    * close(self)        - close socket (Also implies on_close(self) event)

    """
    def __init__(self, factory, address, port, local_address=None):
        self.address = address
        self.port = port
        self.local_address = local_address
        super(ConnectedTCPSocket, self).__init__(factory)

    def __repr__(self):
        return "<%s(0x%x, %s:%s, %s)>" % (
            self.__class__.__name__, id(self),
            self.address, self.port, ", ".join(self.get_flags()))

    def get_label(self):
        return "%s %s:%s" % (self.__class__.__name__,
                             self.address, self.port)

    def create_socket(self):
        self.socket = socket.socket(
            self.get_af(self.address), socket.SOCK_STREAM
        )
        super(ConnectedTCPSocket, self).create_socket()
        if self.local_address:
            self.socket.bind((self.local_address, 0))
        self.logger.debug("Connecting %s:%s", self.address, self.port)
        e = self.socket.connect_ex((self.address, self.port))
        if e in (ETIMEDOUT, ECONNREFUSED, ENETUNREACH,
                 EHOSTUNREACH, ENETDOWN):
            self.on_conn_refused()
            self.close()
            return
        elif e not in (0, EISCONN, EINPROGRESS, EALREADY, EWOULDBLOCK):
            raise socket.error, (e, errorcode[e])
        elif e != 0:
            self.logger.debug(
                "create_socket returns non-zero code %s[%s]",
                e, errorcode[e]
            )
        self.set_status(r=self.is_connected, w=not self.is_connected)

    def handle_read(self):
        if not self.is_connected:
            if self.socket_is_ready():
                self.handle_connect()
            return
        try:
            data = self.socket.recv(self.READ_CHUNK)
        except socket.error, why:
            if why[0] in (EINTR, EAGAIN):
                return  # Silently ignore
            elif why[0] in (ECONNREFUSED, EHOSTUNREACH):
                self.logger.error("Connection refused: %s (%s)",
                                  why[1], why[0])
                self.on_conn_refused()
                self.close()
                return
            else:
                self.logger.error("Connection lost: %s (%s)",
                                  why[1], why[0])
                return
        if not data:
            self.close()
            return
        self.update_status()
        if self.protocol_class:
            self.protocol.feed(data)
        else:
            self.on_read(data)

    def handle_write(self):
        if not self.is_connected:
            try:
                self.socket.send("")
            except socket.error, why:
                self.logger.error("Connection refused: %s (%s)",
                                  why[1], why[0])
                self.on_conn_refused()
                self.close()
                return
            self.handle_connect()
            return
        TCPSocket.handle_write(self)

    def on_conn_refused(self):
        pass


