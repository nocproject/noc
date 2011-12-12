# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TCPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Pyhon modules
import socket
## NOC modules
from noc.lib.nbsocket.basesocket import Socket


class TCPSocket(Socket):
    """
    Base class for TCP socket. Should not be used directly,
    use ConnectedTCPSocket and AcceptedTCPSocket subclasses instead.
    """
    protocol_class = None

    def __init__(self, factory, socket=None):
        """
        :param factory: SocketFactory
        :type factory: SocketFactory instance
        :param socket: Optional socket.socket instance
        :type socket: socket.socket
        """
        self.is_connected = False
        self.out_buffer = ""
        if self.protocol_class:
            self.protocol = self.protocol_class(self, self.on_read)
        self.in_shutdown = False
        self.character_mode = False  # Send one character per packet
        super(TCPSocket, self).__init__(factory, socket)

    def create_socket(self):
        """
        Create socket and adjust buffers
        """
        super(TCPSocket, self).create_socket()
        self.adjust_buffers()

    def close(self, flush=False):
        """
        Close socket.

        :param flush: Send collected data before closing, if True,
                      or discard them
        :type flush: Bool
        """
        if flush and self.out_buffer:
            self.in_shutdown = True
        else:
            super(TCPSocket, self).close()

    def handle_write(self):
        """
        Try to send portion or all buffered data
        """
        try:
            sent = self.socket.send(self.out_buffer[:1] if self.character_mode
                                                       else self.out_buffer)
        except socket.error, why:
            self.error("Socket error: %s" % repr(why))
            self.close()
            return
        self.out_buffer = self.out_buffer[sent:]
        if self.in_shutdown and not self.out_buffer:
            self.close()
        self.update_status()

    def handle_connect(self):
        """
        Set is_connected flag and call on_connect()
        """
        self.is_connected = True
        self.on_connect()

    def write(self, msg):
        """
        Save data to internal buffer. Actual send will be performed
        in handle_write() method

        :param msg: Raw data
        :type msg: Str
        """
        self.out_buffer += msg

    def on_read(self, data):
        """
        Called every time new data is avaiable
        """
        pass

    def on_connect(self):
        """
        Called once when socket connects
        """
        pass

    def adjust_buffers(self):
        """
        Adjust socket buffer size

        @todo: get from configuration parameters
        """
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
        pass

    def set_character_mode(self, status=True):
        """
        Set character mode
        """
        self.debug("%s character mode" % {
            True: "Entering", False: "Leaving"}[status])
        self.character_mode = status
