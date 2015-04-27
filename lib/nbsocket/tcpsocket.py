# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TCPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Pyhon modules
import socket
import errno
## NOC modules
from basesocket import Socket
from exceptions import BrokenPipeError


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
        self.so_sndbuf = None  # Save SO_SNDBUF after entering character mode
        super(TCPSocket, self).__init__(factory, socket)

    def get_flags(self):
        f = super(TCPSocket, self).get_flags()
        if self.is_connected:
            f += ["connected"]
        if self.in_shutdown:
            f += ["shutdown"]
        return f

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
            self.logger.debug("Shutting down socket")
            self.in_shutdown = True
        else:
            self.is_connected = False
            super(TCPSocket, self).close()

    def handle_write(self):
        """
        Try to send portion or all buffered data
        """
        try:
            if self.character_mode:
                self.logger.debug("Character send: %s", self.out_buffer[0])
            if self.character_mode:
                sent = self.socket.send(self.out_buffer[0])
            else:
                sent = self.socket.send(self.out_buffer)
        except socket.error, why:
            self.logger.error("Socket error: %s", repr(why))
            self.close()
            return
        self.out_buffer = self.out_buffer[sent:]
        if self.in_shutdown and not self.out_buffer:
            self.close(flush=True)
            return
        self.set_status(w=bool(self.out_buffer))
        self.update_status()

    def handle_connect(self):
        """
        Set is_connected flag and call on_connect()
        """
        self.logger.debug("Connected")
        self.is_connected = True
        self.set_status(r=True, w=bool(self.out_buffer))
        self.on_connect()

    def write(self, msg):
        """
        Save data to internal buffer. Actual send will be performed
        in handle_write() method

        :param msg: Raw data
        :type msg: str
        """
        if self.closing:
            self.logger.error("Attempting to write to closing socket")
            self.out_buffer += msg
            if self.out_buffer and self.socket:
                # Try to send
                try:
                    self.socket.send(self.out_buffer)
                except socket.error, why:
                    self.logger.error("Failed to send rest of the buffer: %s", repr(why))
            return
        # Try to send immediately
        if self.socket and not self.character_mode and not self.out_buffer:
            try:
                sent = self.socket.send(msg)
                msg = msg[sent:]
            except socket.error, why:
                if why[0] not in (errno.EAGAIN, errno.EINTR,
                                  errno.ENOBUFS, errno.ENOTCONN):
                    self.logger.error("Socket error: %s", repr(why))
                    self.close()
                    return
        self.out_buffer += msg
        self.set_status(w=bool(self.out_buffer) and self.is_connected)

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
        if status:
            # Entering character mode
            self.logger.debug("Entering character mode")
            self.character_mode = True
            # Save SNDBUF size
            self.so_sndbuf = self.socket.getsockopt(socket.SOL_SOCKET,
                                                    socket.SO_SNDBUF)
            # Change SNDBUF to 1
            # To disable buffering
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1)
        else:
            # Leaving character mode
            self.logger.debug("Leaving character mode")
            self.character_mode = False
            # Restore SNDBUF
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,
                                   self.so_sndbuf)
