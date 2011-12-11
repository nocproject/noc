# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Clean and lightweight non-blocking socket I/O implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import socket
import time
import logging
from errno import *
## NOC modules
from noc.lib.nbsocket.exceptions import *
## Try to load SSL module
try:
    import ssl
    HAS_SSL = True
except ImportError:
    HAS_SSL = False


class Socket(object):
    """
    Abstract non-blocking socket wrapper
    """
    TTL = None  # maximum time to live in seconds
    READ_CHUNK = 65536  # @todo: configuration parameter

    def __init__(self, factory, socket=None):
        self.factory = factory
        self.socket = socket
        self.start_time = time.time()
        self.last_read = self.start_time + 100  # @todo: Meaningful value
        self.name = None
        self.ttl = self.TTL
        self.set_timeout(self.TTL)
        self.factory.register_socket(self)

    def create_socket(self):
        """
        Performs actial socket creation and initialization
        and pust socket into nonblocking mode.
        """
        if not self.socket_is_ready():  # Socket was not created
            raise SocketNotImplemented()
        self.socket.setblocking(0)
        self.update_status()

    def set_timeout(self, ttl):
        """
        Change socket timeout

        :param ttl: Timeout in seconds
        :type ttl: Int
        """
        if ttl and ttl != self.ttl:
            self.debug("Set timeout to %s secs" % ttl)
            self.ttl = ttl

    def socket_is_ready(self):
        """
        Check socket is created and ready for operation

        :rtype: Bool
        """
        return self.socket is not None

    def fileno(self):
        """
        Get socket system file id

        :return: file id or None
        :rtype: Int or None
        """
        return self.socket.fileno() if socket else None

    def can_read(self):
        """
        Check socket can be read. If can_read returns True, socket
        will be polled for read event. handle_read() will be called
        when some data will be available for reading

        :rtype: Bool
        """
        return self.socket_is_ready()

    def can_write(self):
        """
        Check socket can be written. If can_write returns True, socket
        will be polled for write events. handle_write() will be called
        when some data can be sent via socket

        :trype bool:
        """
        return self.socket_is_ready()

    def handle_read(self):
        """
        Read handler. Called every time when socket has data available
        to be reading.
        """
        pass

    def handle_write(self):
        """
        Read handler. Called every time when socket has data available
        to be written.
        """
        pass

    def on_close(self):
        """
        Close handler. Called on socket close.
        """
        pass

    def on_error(self, exc):
        """
        Error handler. Called on eny socket error.
        Default behavior is to emit error message and close the socket

        :param exc: SocketException instance
        """
        self.error(exc.message)
        self.close()

    def close(self):
        """
        Close socket and unregister from factory
        """
        if self.socket:
            self.factory.unregister_socket(self)
            try:
                if self.socket:
                    self.socket.close()  # Can raise EBADF/EINTR
            except socket.error, why:
                pass
            self.socket = None
            self.on_close()

    def log_label(self):
        """
        Returns a prefix for log messages

        :rtype: Str
        """
        return "%s(0x%x)" % (self.__class__.__name__, id(self))

    def debug(self, msg):
        """
        Emit debug-level log message.

        :param msg: Message
        :type msg: String
        """
        logging.debug("[%s] %s" % (self.log_label(), msg))

    def info(self, msg):
        """
        Emit info-level log message.

        :param msg: Message
        :type msg: String
        """
        logging.info("[%s] %s" % (self.log_label(), msg))

    def error(self, msg):
        """
        Emit error-level log message.

        :param msg: Message
        :type msg: String
        """

        logging.error("[%s] %s" % (self.log_label(), msg))

    def set_name(self, name):
        """
        Set socket name.

        :param name: Name
        :type name: str
        """
        self.name = name
        self.factory.register_socket(self, name)

    def update_status(self):
        """
        Update socket status to indicate socket still active
        """
        self.last_read = time.time()

    def is_stale(self):
        """
        Check socket is stale.
        Called by SocketFactory.close_stale to determine
        should socket be closed forcefully

        :rtype: Bool
        """
        return (self.socket_is_ready() and self.ttl
                and time.time() - self.last_read >= self.ttl)


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
        :type factory: SocketFactory instance
        :param address: Address to listen on
        :type address: Str
        :param port: Port to listen on
        :type port: Int
        :param socket_class: Socket class to spawn on each new connect
        :type socket_class: AcceptedTCPSocket
        :param backlog: listen() backlog (default 100)  @todo: get from config
        :type backlog: Int
        :param nconnects: Close socket after _nconnects_ connections, if set
        :type nconnects: Int or None
        """
        self.backlog = backlog
        self.nconnects = nconnects
        Socket.__init__(self, factory)
        self.socket_class = socket_class
        self.address = address
        self.port = port
        self.kwargs = kwargs
    
    def create_socket(self):
        """Create socket, bind and listen"""
        if self.socket:  # Called twice
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
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
            if self.nconnects == 0:
                self.close()
    
    def log_label(self):
        """Customized logging prefix"""
        return "%s(0x%x,%s:%s)" % (self.__class__.__name__, id(self),
                                   self.address, self.port)
    

class ListenUDPSocket(Socket):
    """
    UDP Listener. Wait for UDP packet on specified address and port
    and call .on_read() for each packet received.
    """
    def __init__(self, factory, address, port):
        """
        :param factory: SocketFactory
        :type factory: SocketFactory instance
        :param address: Address to listen on
        :type address: Str
        :param port: Port to listen on
        :type port: Int
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
        :type data: Str
        :param address: Source address
        :type address: Str
        :param port: Source port
        :type port: Int
        """
        pass
    
    def can_write(self):
        """
        Indicate data can be written into socket.
        """
        return False


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
        if flush and len(self.out_buffer) > 0:
            self.in_shutdown = True
        else:
            super(TCPSocket, self).close()
    
    def handle_write(self):
        """
        Try to send portion or all buffered data
        """
        try:
            sent = self.socket.send(self.out_buffer)
        except socket.error, why:
            self.error("Socket error: %s" % repr(why))
            self.close()
            return
        self.out_buffer = self.out_buffer[sent:]
        if self.in_shutdown and len(self.out_buffer) == 0:
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
    
    def can_write(self):
        """
        Indicate socket has data to be send
        
        :rtype: Bool
        """
        return len(self.out_buffer) > 0
    

class AcceptedTCPSSLSocket(AcceptedTCPSocket):
    """
    SSL-aware version of AcceptedTCPSocket
    """
    def __init__(self, factory, socket, cert):
        socket = ssl.wrap_socket(socket, server_side=True,
                                 do_handshake_on_connect=False,
                                 keyfile=cert, certfile=cert,
                                 ssl_version=ssl.PROTOCOL_TLSv1)
        self.ssl_handshake_passed = False
        TCPSocket.__init__(self, factory, socket)
    
    def handle_read(self):
        """
        Process SSL handshake or incoming data
        """
        if self.ssl_handshake_passed:
            super(AcceptedTCPSSLSocket, self).handle_read()
        else:  # Process SSL Handshake
            try:
                self.socket.do_handshake()
                self.ssl_handshake_passed = True
                self.debug("SSL Handshake passed: %s" % str(self.socket.cipher()))
                self.handle_connect()  # handle_connect called after SSL negotiation
            except ssl.SSLError, err:
                if err.args[0] in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                    # Incomplete handshake data
                    return
                logging.error("SSL Handshake failed: %s" % err[1])
                self.close()
    

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
        super(ConnectedTCPSocket, self).__init__(factory)
        self.address = address
        self.port = port
        self.local_address = local_address
    
    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        super(ConnectedTCPSocket, self).create_socket()
        if self.local_address:
            self.socket.bind((self.local_address, 0))
        self.debug("Connecting %s:%s" % (self.address, self.port))
        e = self.socket.connect_ex((self.address, self.port))
        if e in (ETIMEDOUT, ECONNREFUSED, ENETUNREACH):
            self.on_conn_refused()
            self.close()
            return
        elif e not in (0, EISCONN, EINPROGRESS, EALREADY, EWOULDBLOCK):
            raise socket.error, (e, errorcode[e])
        
    def handle_read(self):
        if not self.is_connected:
            self.debug("Connected")
            self.handle_connect()
            return
        try:
            data = self.socket.recv(self.READ_CHUNK)
        except socket.error, why:
            if why[0] == ECONNREFUSED:
                self.on_conn_refused()
                self.close()
                return
            if why[0] in (ECONNRESET, ENOTCONN, ESHUTDOWN, ETIMEDOUT):
                self.close()
                return
            if why[0] in (EINTR, EAGAIN):
                return
            raise socket.error, why
        if not data:
            self.close()
            return
        self.update_status()
        if self.protocol_class:
            self.protocol.feed(data)
        else:
            self.on_read(data)
    
    def can_write(self):
        return len(self.out_buffer) > 0 or not self.is_connected
    
    def handle_write(self):
        if not self.is_connected:
            try:
                self.socket.send("")
            except socket.error, why:
                err_code = why[0]
                if err_code in (EPIPE, ECONNREFUSED, ETIMEDOUT,
                                EHOSTUNREACH, ENETUNREACH):
                    self.on_conn_refused()
                    self.close()
                    return
                raise socket.error, why
            self.handle_connect()
            return
        TCPSocket.handle_write(self)
    
    def on_conn_refused(self):
        pass
    

class ConnectedTCPSSLSocket(ConnectedTCPSocket):
    """
    SSL-aware version of ConnectedTCPSocket
    """
    def __init__(self, factory, address, port, local_address=None):
        self.ssl_handshake_passed = False
        super(ConnectedTCPSSLSocket, self).__init__(factory, address, port,
                                                    local_address)

    def handle_connect(self):
        self.socket = ssl.wrap_socket(self.socket, server_side=False,
                                      do_handshake_on_connect=False,
                                      ssl_version=ssl.PROTOCOL_TLSv1)

    def handle_read(self):
        if self.ssl_handshake_passed:
            super(ConnectedTCPSSLSocket, self).handle_read()
        else:  # Process SSL Handshake
            try:
                self.socket.do_handshake()
                self.ssl_handshake_passed = True
                self.debug("SSL Handshake passed: %s" % str(self.socket.cipher()))
            except ssl.SSLError, err:
                if err.args[0] in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                    # Incomplete handshake data
                    return
                raise
