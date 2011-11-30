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
import select
import errno
import time
import logging
import pty
import os
import signal
import subprocess
import sys
import fcntl
from errno import *
from threading import RLock
## NOC modules
from noc.lib.debug import error_report
## Try to load SSL module
try:
    import ssl
    HAS_SSL = True
except ImportError:
    HAS_SSL = False


##
## Exception classes
##
class SocketError(Exception):
    message = "Socket Library Error"


class SocketNotImplemented(Exception):
    message = "Feature not implemented"


class ProtocolNotSupportedError(SocketError):
    message = "The protocol type or the specified protocol "\
              "is not supported within this domain"


class AccessError(SocketError):
    message = "Permission to create a socket "\
              "of the specified type and/or protocol is denied"


class NoFilesError(SocketError):
    message = "Process/System file table is full"


class NoBuffersError(SocketError):
    message = "Insufficient buffer space is available. "\
              "The socket cannot be created until sufficient "\
              "resources are freed."


class ConnectionRefusedError(SocketError):
    message = "Connection Refused"


class NotConnectedError(SocketError):
    message = "The socket is associated with a connection-oriented protocol "\
              "and has not been connected"


class BrokenPipeError(SocketError):
    message = "Broken pipe"


class AccessError(SocketError):
    message = "Permission Denied"


class SocketTimeoutError(SocketError):
    message = "Socket Timeout"


class AddressFamilyError(SocketError):
    message = "Address family for hostname not supported"


class TemporaryResolutionError(SocketError):
    message = "Temporary failure in name resolution"


class NonRecoverableResolutionError(SocketError):
    message = "Non-recoverable failure in name resolution"


class NameNotKnownError(SocketError):
    message = "Node name or service name not known"


class NoMemoryError(SocketError):
    message = "Memory allocation failure"


class BadFileError(SocketError):
    message = "Bad File Descriptor"


class AddressInUse(SocketError):
    message = "Address already in use"


##
## Error name to Exception class mapping
## Used to populate SOCKET_ERROR_TO_EXCEP
##
SOCKET_ERRORS = [
    ("EPROTONOSUPPORT", ProtocolNotSupportedError),
    ("EACCESS", AccessError),
    ("EMFILE", NoFilesError),
    ("ENFILE", NoFilesError),
    ("ENOBUFS", NoBuffersError),
    ("ECONNREFUSED", ConnectionRefusedError),
    ("ENOTCONN", NotConnectedError),
    ("EPIPE", BrokenPipeError),
    ("EACCES", AccessError),
    ("EBADF", BadFileError),
    ("EADDRINUSE", AddressInUse),
]

SOCKET_GAIERROR = [
    ("EAI_ADDRFAMILY", AddressFamilyError),
    ('EAI_AGAIN', TemporaryResolutionError),
    #('EAI_BADFLAGS',),
    ('EAI_FAIL', NonRecoverableResolutionError),
    #('EAI_FAMILY',),
    ('EAI_MEMORY', NoMemoryError),
    #('EAI_NODATA',),
    ('EAI_NONAME', NameNotKnownError),
    #('EAI_SERVICE',),
    #('EAI_SOCKTYPE',),
    #('EAI_SYSTEM',),
]
##
## socket.error to Exception class mapping
##
SOCKET_ERROR_TO_EXCEPTION = {}
for error_name, exception_class in SOCKET_ERRORS:
    try:
        c = getattr(errno, error_name)
        SOCKET_ERROR_TO_EXCEPTION[c] = exception_class
    except AttributeError:
        pass

##
## socket.gaierror to Exception class mapping
##
GAIERROR_TO_EXCEPTION = {}
for error_name, exception_class in SOCKET_GAIERROR:
    try:
        c = getattr(socket, error_name)
        GAIERROR_TO_EXCEPTION[c] = exception_class
    except AttributeError:
        pass


def get_socket_error():
    """
    Check wrether the exception was caused by socket error

    :returns: SocketException instance or None if it is not an socket error
    """
    t, v, tb = sys.exc_info()
    if not t:
        return None
    if t == socket.error:
        try:
            return SOCKET_ERROR_TO_EXCEPTION[v.args[0]]()
        except KeyError:
            return None
    elif t == socket.gaierror:
        try:
            return GAIERROR_TO_EXCEPTION[v.args[0]]()
        except KeyError:
            return None
    elif t == socket.timeout:
        return SocketTimeoutError()
    return None


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
        :type name: Str
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


class Protocol(object):
    """
    Abstract protocol parser. Accepts raw data via feed() method,
    populating internal buffer and calling parse_pdu()
    """
    def __init__(self, parent, callback):
        """
        :param parent: Socket instance
        :param callback: Callable accepting single pdu argument
        """
        self.parent = parent
        self.callback = callback
        self.in_buffer = ""

    def feed(self, data):
        """
        Feed raw data into protocols. Calls callback for each
        completed PDU.

        :param data: Raw data portion
        :type data: Str
        """
        self.in_buffer += data
        for pdu in self.parse_pdu():
            self.callback(pdu)

    def parse_pdu(self):
        """
        Scan self.in_buffer, detect all completed PDUs, then remove
        them from buffer and return as list or yield them

        :return: List of PDUs
        :rtype: List of Str
        """
        return []


class LineProtocol(Protocol):
    """
    Simple line-based protocols. PDUs are separated by "\n"
    """
    def parse_pdu(self):
        pdus = self.in_buffer.split("\n")
        self.in_buffer = pdus.pop(-1)
        return pdus
    

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
        return len(self.out_buffer) > 0
    
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
    

class FileWrapper(object):
    """
    Wrap file to mimic socket behavior. Used in conjunction
    with Socket object
    """
    def __init__(self, fileno):
        self._fileno = fileno
    
    def fileno(self):
        return self._fileno
    
    def recv(self, *args):
        return os.read(self._fileno, *args)
    
    def send(self, *args):
        return os.write(self._fileno, *args)
    
    read = recv
    
    write = send
    
    def close(self):
        os.close(self._fileno)
    
    def setblocking(self, status):
        """
        Set blocking status
        
        :param staus: 0 - non-blocking mode, 1 - blocking mode
        """
        flags = fcntl.fcntl(self._fileno, fcntl.F_GETFL, 0)
        if status:
            flags = flags & (0xFFFFFFFF ^ os.O_NONBLOCK)  # Blocking mode
        else:
            flags = flags | os.O_NONBLOCK  # Nonblocking mode
        fcntl.fcntl(self._fileno, fcntl.F_SETFL, flags)
    

class PTYSocket(Socket):
    """
    Wrap PTY to mimic socket behavior
    """
    def __init__(self, factory, argv):
        self.pid = None
        self.argv = argv
        self.out_buffer = ""
        super(PTYSocket, self).__init__(factory)
    
    def create_socket(self):
        self.debug("EXECV(%s)" % str(self.argv))
        try:
            self.pid, fd = pty.fork()
        except OSError:
            self.debug("Cannot get PTY. Closing")
            self.close()
            return
        if self.pid == 0:
            os.execv(self.argv[0], self.argv)
        else:
            self.socket = FileWrapper(fd)
            super(PTYSocket, self).create_socket()
    
    def handle_read(self):
        try:
            data = self.socket.read(self.READ_CHUNK)
        except OSError:
            self.close()
            return
        self.update_status()
        if data:
            self.on_read(data)
        else:
            self.close()
    
    def can_write(self):
        return len(self.out_buffer) > 0
    
    def handle_write(self):
        sent = self.socket.send(self.out_buffer)
        self.out_buffer = self.out_buffer[sent:]
    
    def handle_connect(self):
        self.is_connected = True
        self.on_connect()
    
    def write(self, msg):
        self.debug("write(%s)" % repr(msg))
        self.out_buffer += msg
    
    def close(self, flush=False):
        Socket.close(self)
        if self.pid is None:
            return
        try:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
        except os.error:
            return
        if pid:
            self.debug("Child pid=%d is already terminated. Zombie released" % pid)
        else:
            self.debug("Child pid=%d is not terminated. Killing" % self.pid)
            try:
                os.kill(self.pid, signal.SIGKILL)
            except:
                self.debug("Child pid=%d was killed from another place" % self.pid)
    
    def on_read(self, data):
        pass
    

class PopenSocket(Socket):
    """
    Wrap popen() call to mimic socket behavior
    """
    def __init__(self, factory, argv):
        super(PopenSocket, self).__init__(factory)
        self.argv = argv
        self.update_status()
    
    def create_socket(self):
        self.debug("Launching %s" % self.argv)
        self.p = subprocess.Popen(self.argv, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.socket = FileWrapper(self.p.stdout.fileno())
    
    def handle_read(self):
        try:
            data = self.socket.read(self.READ_CHUNK)
        except OSError:
            self.close()
            return
        self.update_status()
        if data:
            self.on_read(data)
        else:
            self.close()
    
    def close(self, flush=False):
        Socket.close(self)
    

class SocketFactory(object):
    """
    Socket factory is a major event loop controller, maintaining full socket
    lifetime
    """
    def __init__(self, tick_callback=None, polling_method=None, controller=None):
        self.sockets = {}      # fileno -> socket
        self.socket_name = {}  # socket -> name
        self.name_socket = {}  # name -> socket
        self.new_sockets = []  # list of (socket,name)
        self.tick_callback = tick_callback
        self.to_shutdown = False
        self.register_lock = RLock()    # Guard for register/unregister operations
        self.controller = controller    # Reference to controlling daemon
        self.get_active_sockets = None  # Polling method
        self.setup_poller(polling_method)
        # Performance data
        self.cnt_polls = 0  # Number of polls
    
    def shutdown(self):
        """
        Shut down socket factory and exit next event loop
        """
        logging.info("Shutting down the factory")
        self.to_shutdown = True
    
    # Check select() available
    def has_select(self):
        """
        Check select() method is available
        
        :rtype: Bool
        """
        return True
    
    def has_kevent(self):
        """
        Check kevent/kqueue method is available
        
        :rtype: Bool
        """
        return hasattr(select, "kqueue")
    
    def has_poll(self):
        """
        Check poll() method is available
        
        :rtype: Bool
        """
        return hasattr(select, "poll")
    
    def has_epoll(self):
        """
        Check epoll() method is available
        
        :rtype: Bool
        """
        return hasattr(select, "epoll")
    
    def setup_poller(self, polling_method=None):
        """
        Set up polling function.
        
        :param polling_method: Name of polling method. Must be one of:
                               * select
                               * poll
                               * kevent
                               * epoll
                               * None (detect best method)
        """
        def setup_select_poller():
            """Enable select() method"""
            logging.debug("Set up select() poller")
            self.get_active_sockets = self.get_active_select
            self.polling_method = "select"
        
        def setup_poll_poller():
            """Enable poll() method"""
            logging.debug("Set up poll() poller")
            self.get_active_sockets = self.get_active_poll
            self.polling_method = "poll"
        
        def setup_epoll_poller():
            """Enable epoll() method"""
            logging.debug("Set up epoll() poller")
            self.get_active_sockets = self.get_active_epoll
            self.polling_method = "epoll"
        
        def setup_kevent_poller():
            """Enable kevent() method. Broken for now and disabled"""
            logging.debug("Set up kevent/kqueue poller")
            self.get_active_sockets = self.get_active_kevent
            self.polling_method = "kevent"
        
        if polling_method is None:
            # Read settings if available
            try:
                from noc.settings import config
                polling_method = config.get("main", "polling_method")
            except ImportError:
                polling_method = "select"
        logging.debug("Setting up '%s' polling method" % polling_method)
        if polling_method == "optimal":
            # Detect possibilities
            if self.has_kevent():  # kevent
                setup_kevent_poller()
            elif self.has_epoll():
                setup_epoll_poller()  # epoll
            elif self.has_poll():  # poll
                setup_poll_poller()
            else:  # Fallback to select
                setup_select_poller()
        elif polling_method == "kevent" and self.has_kevent():
            setup_kevent_poller()
        elif polling_method == "epoll" and self.has_epoll():
            setup_epoll_poller()
        elif polling_method == "poll" and self.has_poll():
            setup_poll_poller()
        else:
            # Fallback to select
            setup_select_poller()
    
    def register_socket(self, socket, name=None):
        """
        Register socket to a factory. Socket became a new socket
        """
        logging.debug("register_socket(%s,%s)" % (socket, name))
        with self.register_lock:
            self.new_sockets += [(socket, name)]
    
    def unregister_socket(self, socket):
        """
        Remove socket from factory
        """
        with self.register_lock:
            logging.debug("unregister_socket(%s)" % socket)
            if socket not in self.socket_name:  # Not in factory yet
                return
            self.sockets.pop(socket.fileno(), None)
            old_name = self.socket_name.pop(socket, None)
            self.name_socket.pop(old_name, None)
            if socket in self.new_sockets:
                self.new_sockets.remove(socket)
    
    def guarded_socket_call(self, socket, method):
        """
        Wrapper for safe call of socket method. Handles and reports
        socket errors.
        
        :return: Call status
        :rtype: Bool
        """
        try:
            method()
        except:
            exc = get_socket_error()
            try:
                if exc:
                    socket.on_error(exc)
                else:
                    socket.error("Unhandled exception when calling %s" % str(method))
                    error_report()
                    socket.close()
            except:
                socket.error("Error when handling error condition")
                error_report()
            return False
        return True
    
    def init_socket(self, socket, name):
        """
        Initialize new socket. Call socket's create_socket() when necessary
        and attach socket to fabric's event loop
        """
        if not socket.socket_is_ready():
            socket.debug("Initializing socket")
            if not self.guarded_socket_call(socket, socket.create_socket):
                return
        if socket.socket is None:
            # Race condition raised. Socket is unregistered since last socket.create_socket call.
            # Silently ignore and exit
            return
        with self.register_lock:
            self.sockets[socket.fileno()] = socket
            if socket in self.socket_name:
                # Socket was registred
                old_name = self.socket_name[socket]
                del self.socket_name[socket]
                if old_name:
                    del self.name_socket[old_name]
            self.socket_name[socket] = name
            if name:
                self.name_socket[name] = socket
    
    def listen_tcp(self, address, port, socket_class, backlog=100,
                   nconnects=None, **kwargs):
        """Create listening TCP socket"""
        if not issubclass(socket_class, AcceptedTCPSocket):
            raise "socket_class should be a AcceptedTCPSocket subclass"
        l = ListenTCPSocket(self, address, port, socket_class, backlog,
                            nconnects, **kwargs)
        l.set_name("listen-tcp-%s:%d" % (address, port))
        return l
    
    def connect_tcp(self, address, port, socket_class):
        """Create ConnectedTCPSocket"""
        if not issubclass(socket_class, ConnectedTCPSocket):
            raise "socket_class should be a ConnectedTCPSocket subclass"
        return socket_class(self, address, port)
    
    def get_socket_by_name(self, name):
        """Get socket by registered name"""
        with self.register_lock:
            return self.name_socket[name]
    
    def get_name_by_socket(self, socket):
        """Get socket name by instance"""
        with self.register_lock:
            return self.socket_name[socket]
    
    def __len__(self):
        """Returns a number of factory's sockets"""
        with self.register_lock:
            return len(self.sockets)
    
    def close_stale(self):
        """Detect and close stale sockets"""
        with self.register_lock:
            for s in [s for s in self.sockets.values() if s.is_stale()]:
                logging.debug("Closing stale socket %s" % s)
                s.close()
    
    def create_pending_sockets(self):
        """Initialize pending sockets"""
        with self.register_lock:
            while self.new_sockets:
                socket, name = self.new_sockets.pop(0)
                self.init_socket(socket, name)
    
    def loop(self, timeout=1):
        """
        Generic event loop. Depends upon get_active_sockets() method, set
        up by factory constructor
        """
        self.create_pending_sockets()
        if self.sockets:
            r, w = self.get_active_sockets(timeout)
            self.cnt_polls += 1
            #logging.debug("Active sockets: Read=%s Write=%s"%(repr(r), repr(w)))
            # Process write events before read to catch refused connections
            for fd in w:
                s = self.sockets.get(fd)
                if s:
                    self.guarded_socket_call(s, s.handle_write)
            # Process read events
            for fd in r:
                s = self.sockets.get(fd)
                if s:
                    self.guarded_socket_call(s, s.handle_read)
        else:
            # No socket initialized. Sleep to prevent CPU hogging
            time.sleep(timeout)
    
    ##
    ## Straightforward select() implementation
    ## Returns a list of (read fds, write fds)
    ##
    def get_active_select(self, timeout):
        """
        select() implementation
        
        :returns: Tuple of (List of read socket ids, Write socket ids)
        """
        # Get read and write candidates
        with self.register_lock:
            r = [f for f, s in self.sockets.items() if s.can_read()]
            w = [f for f, s in self.sockets.items() if s.can_write()]
        # Poll socket status
        try:
            r, w, x = select.select(r, w, [], timeout)
            return r, w
        except select.error, why:
            if why[0] not in (EINTR, EBADF):
                error_report()  # non-ignorable errors
            return [], []
        except KeyboardInterrupt:
            logging.info("Got Ctrl+C, exiting")
            sys.exit(0)
        except:
            error_report()
            return [], []
    
    def get_active_poll(self, timeout):
        """
        poll() implementation
        
        :returns: Tuple of (List of read socket ids, Write socket ids)
        """
        poll = select.poll()
        # Get read and write candidates
        with self.register_lock:
            for f, s in self.sockets.items():
                e = ((select.POLLIN if s.can_read() else 0) |
                     (select.POLLOUT if s.can_write() else 0))
                if e:
                    poll.register(f, e)
        # Poll socket status
        try:
            events = poll.poll(timeout * 1000)  # ms->s
        except select.error, why:
            if why[0] not in (EINTR, EBADF):
                error_report()  # non-ignorable errors
            return [], []
        except:
            return [], []
        # Build result
        rset = [fd for fd, e in events if e & (select.POLLIN | select.POLLHUP)]
        wset = [fd for fd, e in events if e & select.POLLOUT]
        return rset, wset
    
    def get_active_kevent(self, timeout):
        """
        kevent() implementation. Broken.
        
        :returns: Tuple of (List of read socket ids, Write socket ids)
        """
        # Get read and write candidates
        kqueue = select.kqueue()
        l = 0
        with self.register_lock:
            for f, s in self.sockets.items():
                if s.can_write():
                    kqueue.control([select.kevent(f, select.KQ_FILTER_WRITE,
                                                  select.KQ_EV_ADD)], 0)
                    l += 1
                if s.can_read():
                    kqueue.control([select.kevent(f, select.KQ_FILTER_READ,
                                                  select.KQ_EV_ADD)], 0)
                    l += 1
        # Poll events
        rset = []
        wset = []
        for e in kqueue.control(None, l, timeout):
            if e.filter & select.KQ_FILTER_WRITE:
                wset += [e.ident]
            if e.filter & select.KQ_FILTER_READ:
                rset += [e.ident]
        return rset, wset
    
    def get_active_epoll(self, timeout):
        """
        epoll() implementation
        
        :returns: Tuple of (List of read socket ids, Write socket ids)
        """
        
        epoll = select.epoll()
        # Get read and write candidates
        with self.register_lock:
            for f, s in self.sockets.items():
                e = ((select.EPOLLIN if s.can_read() else 0) |
                     (select.EPOLLOUT if s.can_write() else 0))
                if e:
                    epoll.register(f, e)
        # Poll socket status
        try:
            events = epoll.poll(timeout)
        except select.error, why:
            if why[0] not in (EINTR, EBADF):
                error_report()  # non-ignorable errors
            return [], []
        except:
            return [], []
        # Build result
        rset = [fd for fd, e in events if e & (select.EPOLLIN | select.EPOLLHUP)]
        wset = [fd for fd, e in events if e & select.EPOLLOUT]
        return rset, wset
    
    def run(self, run_forever=False):
        """
        Socket factory event loop.
        
        :param run_forever: Run event loop forever, when True, else shutdown
                            fabric when no sockets available
        """
        logging.debug("Running socket factory")
        self.create_pending_sockets()
        if run_forever:
            cond = lambda: True
        else:
            cond = lambda: len(self.sockets) > 0
            # Wait for any socket
            while not cond():
                time.sleep(1)
        last_tick = last_stale = time.time()
        while cond() and not self.to_shutdown:
            self.loop(1)
            t = time.time()
            if self.tick_callback and t - last_tick >= 1:
                try:
                    self.tick_callback()
                except:
                    error_report()
                    logging.info("Restoring from tick() failure")
                last_tick = t
            if t - last_stale > 3:
                self.close_stale()
                last_stale = t
