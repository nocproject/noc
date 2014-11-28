# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ListenTCPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
## NOC modules
from noc.lib.nbsocket.basesocket import Socket


class ListenTCPSocket(Socket):
    """
    TCP Listener. Waits for connection and creates socket_class instance.
    Should not be used directly. SocketFactory.listen_tcp() method
    is preferred
    """
    def __init__(self, factory, address, port, socket_class, backlog=100,
                 nconnects=None, **kwargs):
        """
        :param factory: Socket Factory
        :type factory: SocketFactory
        :param address: Address to listen on
        :type address: str
        :param port: Port to listen on
        :type port: int
        :param socket_class: Socket class to spawn on each new connect
        :type socket_class: AcceptedTCPSocket
        :param backlog: listen() backlog (default 100)  @todo: get from config
        :type backlog: int
        :param nconnects: Close socket after _nconnects_ connections, if set
        :type nconnects: int or None
        """
        self.backlog = backlog
        self.nconnects = nconnects
        self.socket_class = socket_class
        self.address = address
        self.port = port
        self.kwargs = kwargs
        Socket.__init__(self, factory)

    def __repr__(self):
        return "<%s(0x%x, %s:%s)>" % (
            self.__class__.__name__, id(self), self.address, self.port)

    def get_label(self):
        return "%s %s:%s" % (
            self.__class__.__name__,
            "*" if self.address == "0.0.0.0" else self.address,
            self.port
        )

    def create_socket(self):
        """Create socket, bind and listen"""
        if self.socket:  # Called twice
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) | 1)
        self.socket.bind((self.address, self.port))
        self.socket.listen(self.backlog)
        super(ListenTCPSocket, self).create_socket()

    def handle_read(self):
        """Handle new connections."""
        s, addr = self.socket.accept()
        if self.socket_class.check_access(addr[0]):
            self.socket_class(self.factory, s, **self.kwargs)
        else:
            self.error("Refusing connection from %s" % addr[0])
            s.close()
        if self.nconnects is not None:
            self.nconnects -= 1
            if not self.nconnects:
                self.close()
