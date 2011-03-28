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
    HAS_SSL=True
except ImportError:
    HAS_SSL=False

##
## Exception classes
##
class SocketError(Exception):
    message="Socket Library Error"

class SocketNotImplemented(Exception):
    message="Feature not implemented"

class ProtocolNotSupportedError(SocketError):
    message="The protocol type or the specified protocol is not supported within this domain"

class AccessError(SocketError):
    message="Permission to create a socket of the specified type and/or protocol is denied"

class NoFilesError(SocketError):
    message="Process/System file table is full"

class NoBuffersError(SocketError):
    message="Insufficient buffer space is available.  The socket cannot be created until sufficient resources are freed."

class ConnectionRefusedError(SocketError):
    message="Connection Refused"

class NotConnectedError(SocketError):
    message="The socket is associated with a connection-oriented protocol and has not been connected"

class BrokenPipeError(SocketError):
    message="Broken pipe"

class AccessError(SocketError):
    message="Permission Denied"

class SocketTimeoutError(SocketError):
    message="Socket Timeout"

class AddressFamilyError(SocketError):
    message="Address family for hostname not supported"

class TemporaryResolutionError(SocketError):
    message="Temporary failure in name resolution"

class NonRecoverableResolutionError(SocketError):
    message="Non-recoverable failure in name resolution"

class NameNotKnownError(SocketError):
    message="Node name or service name not known"

class NoMemoryError(SocketError):
    message="Memory allocation failure"

class BadFileError(SocketError):
    message="Bad File Descriptor"

class AddressInUse(SocketError):
    message="Address already in use"

##
## Error name to Exception class mapping
## Used to populate SOCKET_ERROR_TO_EXCEP
##
SOCKET_ERRORS=[
    ("EPROTONOSUPPORT", ProtocolNotSupportedError),
    ("EACCESS",         AccessError),
    ("EMFILE",          NoFilesError),
    ("ENFILE",          NoFilesError),
    ("ENOBUFS",         NoBuffersError),
    ("ECONNREFUSED",    ConnectionRefusedError),
    ("ENOTCONN",        NotConnectedError),
    ("EPIPE",           BrokenPipeError),
    ("EACCES",          AccessError),
    ("EBADF",           BadFileError),
    ("EADDRINUSE",      AddressInUse),
]

SOCKET_GAIERROR=[
    ("EAI_ADDRFAMILY", AddressFamilyError),
    ('EAI_AGAIN',      TemporaryResolutionError),
    #('EAI_BADFLAGS',),
    ('EAI_FAIL',       NonRecoverableResolutionError),
    #('EAI_FAMILY',),
    ('EAI_MEMORY',     NoMemoryError),
    #('EAI_NODATA',),
    ('EAI_NONAME',     NameNotKnownError),
    #('EAI_SERVICE',),
    #('EAI_SOCKTYPE',),
    #('EAI_SYSTEM',),
]
##
## socket.error to Exception class mapping
##
SOCKET_ERROR_TO_EXCEPTION={}
for error_name,exception_class in SOCKET_ERRORS:
    try:
        c=getattr(errno,error_name)
        SOCKET_ERROR_TO_EXCEPTION[c]=exception_class
    except AttributeError:
        pass
##
## socket.gaierror to Exception class mapping
##
GAIERROR_TO_EXCEPTION={}
for error_name,exception_class in SOCKET_GAIERROR:
    try:
        c=getattr(socket,error_name)
        GAIERROR_TO_EXCEPTION[c]=exception_class
    except AttributeError:
        pass
##
## Check wrether the exception was caused by socket error
## Returns SocketException instance
## of None if it was not the socket error
##
def get_socket_error():
    t,v,tb=sys.exc_info()
    if not t:
        return None
    if t==socket.error:
        try:
            return SOCKET_ERROR_TO_EXCEPTION[v.args[0]]()
        except KeyError:
            return None
    elif t==socket.gaierror:
        try:
            return GAIERROR_TO_EXCEPTION[v.args[0]]()
        except KeyError:
            return None
    elif t==socket.timeout:
        return SocketTimeoutError()
    return None
##
## Abstract non-blocking socket wrapper.
##
class Socket(object):
    TTL=None # maximum time to live in seconds
    READ_CHUNK=65536
    def __init__(self,factory,socket=None):
        self.factory=factory
        self.socket=socket
        self.start_time=time.time()
        self.last_read=self.start_time+100
        self.name=None
        self.factory.register_socket(self)
    ##
    ## Performs actual socket creation
    ##
    def create_socket(self):
        if not self.socket_is_ready(): # Socket was not created
            raise SocketNotImplemented()
        self.socket.setblocking(0)
    ##
    ## Returns True when socket created and ready for operation
    ##
    def socket_is_ready(self):
        return self.socket is not None
    
    def can_read(self):
        return self.socket_is_ready()
        
    def can_write(self):
        return self.socket_is_ready()
        
    def handle_read(self):
        pass
        
    def handle_write(self):
        pass
    ##
    ## Called on socket close
    ##
    def on_close(self):
        pass
    ##
    ## Called on any socket error
    ## Issues error message and closes socket
    ## exc - is an SocketException instance
    ##
    def on_error(self,exc):
        self.error(exc.message)
        self.close()
        
    def close(self):
        if self.socket:
            self.factory.unregister_socket(self)
            try:
                self.socket.close() # Can raise EBADF/EINTR
            except:
                pass
            self.socket=None
            self.on_close()
    ##
    ## Returns a label for debug/error methods
    ##
    def log_label(self):
        return "%s(0x%x)"%(self.__class__.__name__,id(self))
    
    def debug(self,msg):
        logging.debug("[%s] %s"%(self.log_label(),msg))
    
    def info(self,msg):
        logging.info("[%s] %s"%(self.log_label(),msg))
    
    def error(self,msg):
        logging.error("[%s] %s"%(self.log_label(),msg))
    
    def set_name(self,name):
        self.name=name
        self.factory.register_socket(self,name)
    ##
    ## Update socket status to indicate socket still alive
    ##
    def update_status(self):
        self.last_read=time.time()
    # Stale sockets detection.
    # Called by SocketFactory.close_stale to determine should socket be closed forcefully
    def is_stale(self):
        return self.socket_is_ready() and self.TTL and time.time()-self.last_read>=self.TTL
##
## Abstract Protocol Parser.
## Accepts data via feed method, polupates internal buffer (self.in_buffer).
## and calls parse_pdu.
## parse_pdu must parse self.in_buffer, retrieve all complete pdu,
## remove them from buffer and return a list of parsed PDU (or empty list if not found)
## All parsed pdu are returned via callback method
class Protocol(object):
    def __init__(self, parent, callback):
        self.parent=parent
        self.callback=callback
        self.in_buffer=""
        
    def feed(self,data):
        self.in_buffer+=data
        for pdu in self.parse_pdu():
            self.callback(pdu)
    
    def parse_pdu(self):
        return []
##
## Line protocol. PDUs are separated by "\n"
##
class LineProtocol(Protocol):
    def on_feed(self):
        pdus=self.in_buffer.split("\n")
        self.in_buffer=pdus.pop(-1)
        return pdus
##
## TCP Listener.
## Waits for connection and creates socket_class instance.
## socket_class should be subclass of AcceptedTCPSocket.
## Should not be used directly. Use SocketFactory.listen_tcp method instead
##
class ListenTCPSocket(Socket):
    def __init__(self,factory, address, port, socket_class, backlog=100, nconnects=None, **kwargs):
        self.backlog=backlog
        self.nconnects=nconnects
        Socket.__init__(self,factory)
        self.socket_class=socket_class
        self.address=address
        self.port=port
        self.kwargs=kwargs
    
    def create_socket(self):
        if self.socket: # Called twice
            return
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,
            self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR) | 1)
        self.socket.bind((self.address,self.port))
        self.socket.listen(self.backlog)
        super(ListenTCPSocket,self).create_socket()
    
    def handle_read(self):
        s,addr=self.socket.accept()
        if self.socket_class.check_access(addr[0]):
            self.socket_class(self.factory,s,**self.kwargs)
        else:
            logging.error("Refusing connection from %s"%addr[0])
            s.close()
        if self.nconnects is not None:
            self.nconnects-=1
            if self.nconnects==0:
                self.close()
    
    def log_label(self):
        return "%s(0x%x,%s:%s)"%(self.__class__.__name__,id(self),self.address,self.port)
##
## UDP Listener
## Waits for UDP packets on specified ports
## and calls on_read for each packet
class ListenUDPSocket(Socket):
    def __init__(self,factory,address,port):
        Socket.__init__(self,factory)
        self.address=address
        self.port=port
    
    def create_socket(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,
            self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR) | 1)
        self.socket.bind((self.address,self.port))
        super(ListenUDPSocket,self).create_socket()
    
    def handle_read(self):
        msg,transport_address=self.socket.recvfrom(self.READ_CHUNK)
        if msg=="":
            return
        self.on_read(msg,transport_address[0],transport_address[1])
    
    def on_read(self,data,address,port):
        pass
    
    def can_write(self):
        return False

##
## Base class for TCP sockets. Should not be used directly.
## Use ConnectedTCPSocket and AcceptedTCPSocket instead
##
class TCPSocket(Socket):
    protocol_class=None
    def __init__(self, factory, socket=None):
        super(TCPSocket,self).__init__(factory, socket)
        self.is_connected=False
        #self.s=socket
        self.out_buffer=""
        if self.protocol_class:
            self.protocol=self.protocol_class(self, self.on_read)
        self.in_shutdown=False
    
    def create_socket(self):
        super(TCPSocket, self).create_socket()
        self.adjust_buffers()
        
    def close(self,flush=False):
        if flush and len(self.out_buffer)>0:
            self.in_shutdown=True
        else:
            super(TCPSocket,self).close()
        
    def handle_write(self):
        try:
            sent=self.socket.send(self.out_buffer)
        except socket.error, why:
            self.error("Socket error: %s"%repr(why))
            self.close()
            return
        self.out_buffer=self.out_buffer[sent:]
        if self.in_shutdown and len(self.out_buffer)==0:
            self.close()
        
    def handle_connect(self):
        self.is_connected=True
        self.on_connect()
        
    def write(self,msg):
        self.debug("write(%s)"%repr(msg))
        self.out_buffer+=msg
        
    def on_read(self,data): pass
    
    def on_connect(self): pass
    
    def adjust_buffers(self):
        #print self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
        pass

##
## A socket wrapping accepted TCP connection.
## Following methods can be overrided for desired behavior:
## check_access(cls, address) - called before object creation
## on_connect(self)   - called when socket connected (just after creation)
## on_close(self)     - called when socket closed. Last method called
## on_read(self,data) - called when new portion of data available when protocol=None or when new PDU available
## Following methods used for operation:
## write(self,data)   - send data (Buffered, can be delayed or split into several send)
## close(self)        - close socket (Also implies on_close(self) event)
##
class AcceptedTCPSocket(TCPSocket):
    def __init__(self,factory,socket):
        super(AcceptedTCPSocket,self).__init__(factory,socket)
        self.handle_connect()
    
    @classmethod
    def check_access(cls,address):
        return True
        
    def handle_read(self):
        try:
            data=self.socket.recv(self.READ_CHUNK)
        except socket.error,why:
            if why[0] in (ECONNRESET,ENOTCONN,ESHUTDOWN):
                self.close()
                return
            if why[0] in (EINTR, EAGAIN):
                return
            raise socket.error, why
        if data=="":
            self.close()
            return
        self.update_status()
        if self.protocol_class:
            self.protocol.feed(data)
        else:
            self.on_read(data)
        
    def can_write(self):
        return len(self.out_buffer)>0
##
## SSL-enabled AcceptedTCPSocket
##
class AcceptedTCPSSLSocket(AcceptedTCPSocket):
    def __init__(self,factory,socket,cert):
        socket=ssl.wrap_socket(socket,server_side=True,do_handshake_on_connect=False,
            keyfile=cert,certfile=cert,
            ssl_version=ssl.PROTOCOL_TLSv1)
        self.ssl_handshake_passed=False
        TCPSocket.__init__(self,factory,socket)
    
    def handle_read(self):
        if self.ssl_handshake_passed:
            super(AcceptedTCPSSLSocket,self).handle_read()
        else: # Process SSL Handshake
            try:
                self.socket.do_handshake()
                self.ssl_handshake_passed=True
                self.debug("SSL Handshake passed: %s"%str(self.socket.cipher()))
                self.handle_connect() # handle_connect called after SSL negotiation
            except ssl.SSLError,err:
                if err.args[0] in [ssl.SSL_ERROR_WANT_READ,ssl.SSL_ERROR_WANT_WRITE]: # Incomplete handshake data
                    return
                logging.error("SSL Handshake failed: %s"%err[1])
                self.close()
##
## A socket wrapping connectiong TCP connection.
## Following methods can be overrided for desired behavior:
## on_connect(self)   - called when connection established and socket read to send data (first event)
## on_close(self)     - called when socket closed. Last method called
## on_read(self,data) - called when new portion of data available
## on_conn_refused(self) - called when connection refused (Also implies close(self). first event)
## Following methods used for operation:
## write(self,data)   - send data (Buffered, can be delayed or split into several send)
## close(self)        - close socket (Also implies on_close(self) event)
##
class ConnectedTCPSocket(TCPSocket):
    def __init__(self, factory, address, port, local_address=None):
        super(ConnectedTCPSocket,self).__init__(factory)
        self.address=address
        self.port=port
        self.local_address=local_address
    
    def create_socket(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        super(ConnectedTCPSocket,self).create_socket()
        if self.local_address:
            self.socket.bind((self.local_address,0))
        e=self.socket.connect_ex((self.address,self.port))
        if e in (ETIMEDOUT, ECONNREFUSED, ENETUNREACH):
            self.on_conn_refused()
            self.close()
            return
        elif e not in (0, EISCONN,EINPROGRESS, EALREADY, EWOULDBLOCK):
            raise socket.error, (e, errorcode[e])
        
    def handle_read(self):
        if not self.is_connected:
            self.handle_connect()
            return
        try:
            data=self.socket.recv(self.READ_CHUNK)
        except socket.error,why:
            if why[0]==ECONNREFUSED:
                self.on_conn_refused()
                self.close()
                return
            if why[0] in (ECONNRESET,ENOTCONN,ESHUTDOWN):
                self.close()
                return
            if why[0] in (EINTR, EAGAIN):
                return
            raise socket.error,why
        if not data:
            self.close()
            return
        self.update_status()
        if self.protocol_class:
            self.protocol.feed(data)
        else:
            self.on_read(data)
    
    def can_write(self):
        return len(self.out_buffer)>0 or not self.is_connected
    
    def handle_write(self):
        if not self.is_connected:
            try:
                self.socket.send("")
            except socket.error,why:
                err_code=why[0]
                if err_code in (EPIPE, ECONNREFUSED, ETIMEDOUT, EHOSTUNREACH, ENETUNREACH):
                    self.on_conn_refused()
                    self.close()
                    return
                raise socket.error,why
            self.handle_connect()
            return
        TCPSocket.handle_write(self)
    
    def on_conn_refused(self): pass
##
##
##
class ConnectedTCPSSLSocket(ConnectedTCPSocket):
    def __init__(self,factory,address,port,local_address=None):
        self.ssl_handshake_passed=False
        super(ConnectedTCPSSLSocket,self).__init__(factory,address,port,local_address)
        self.socket=ssl.wrap_socket(self.socket,server_side=False,do_handshake_on_connect=False,ssl_version=ssl.PROTOCOL_TLSv1)
    
    def handle_read(self):
        if self.ssl_handshake_passed:
            super(ConnectedTCPSSLSocket,self).handle_read()
        else: # Process SSL Handshake
            try:
                self.socket.do_handshake()
                self.ssl_handshake_passed=True
                self.debug("SSL Handshake passed: %s"%str(self.socket.cipher()))
            except ssl.SSLError,err:
                if err.args[0] in [ssl.SSL_ERROR_WANT_READ,ssl.SSL_ERROR_WANT_WRITE]: # Incomplete handshake data
                    return
                raise
##
## UDP send/receive socket
##
class UDPSocket(Socket):
    def __init__(self,factory):
        self.out_buffer=[]
        super(UDPSocket,self).__init__(factory)
    
    def create_socket(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        super(UDPSocket,self).create_socket()
    
    def can_write(self):
        return len(self.out_buffer)>0
    
    def handle_write(self):
        msg,addr=self.out_buffer.pop(0)
        self.socket.sendto(msg,addr)
        self.update_status()

    def handle_read(self):
        self.update_status()
        msg,transport_address=self.socket.recvfrom(self.READ_CHUNK)
        if msg=="":
            return
        self.on_read(msg,transport_address[0],transport_address[1])
    
    def on_read(self,data,address,port):
        pass

    def sendto(self,msg,addr):
        self.out_buffer+=[(msg,addr)]
    
##
## File wrapper to mimic behavior of socket
##
class FileWrapper(object):
    def __init__(self,fileno):
        self._fileno=fileno
    
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
    
    ##
    ## Set blocking status
    ## 0 - non-blocking mode
    ## 1 - blocking mode
    ##
    def setblocking(self, status):
        flags=fcntl.fcntl(self._fileno, fcntl.F_GETFL, 0)
        if status:
            flags = flags & (0xFFFFFFFF^os.O_NONBLOCK) # Blocking mode
        else:
            flags = flags | os.O_NONBLOCK # Nonblocking mode
        fcntl.fcntl(self._fileno, fcntl.F_SETFL, flags)
    

##
## PTY Socket Emulation
## Events: on_read, on_close
##
class PTYSocket(Socket):
    def __init__(self,factory,argv):
        self.pid=None
        self.argv=argv
        self.out_buffer=""
        super(PTYSocket,self).__init__(factory)
    
    def create_socket(self):
        self.debug("EXECV(%s)"%str(self.argv))
        try:
            self.pid,fd=pty.fork()
        except OSError:
            self.debug("Cannot get PTY. Closing")
            self.close()
            return
        if self.pid==0:
            os.execv(self.argv[0],self.argv)
        else:
            self.socket=FileWrapper(fd)
            super(PTYSocket,self).create_socket()
    
    def handle_read(self):
        try:
            data=self.socket.read(self.READ_CHUNK)
        except OSError:
            self.close()
            return
        self.update_status()
        if data:
            self.on_read(data)
        else:
            self.close()

    def can_write(self):
        return len(self.out_buffer)>0
        
    def handle_write(self):
        sent=self.socket.send(self.out_buffer)
        self.out_buffer=self.out_buffer[sent:]

    def handle_connect(self):
        self.is_connected=True
        self.on_connect()

    def write(self,msg):
        self.debug("write(%s)"%repr(msg))
        self.out_buffer+=msg
    
    def close(self, flush=False):
        Socket.close(self)
        if self.pid is None:
            return
        try:
            pid,status=os.waitpid(self.pid,os.WNOHANG)
        except os.error:
            return
        if pid:
            self.debug("Child pid=%d is already terminated. Zombie released"%pid)
        else:
            self.debug("Child pid=%d is not terminated. Killing"%self.pid)
            try:
                os.kill(self.pid,signal.SIGKILL)
            except:
                self.debug("Child pid=%d was killed from another place"%self.pid)
    
    def on_read(self,data):
        pass
##
## PopenSocket
## Events: on_read, on_close
##
class PopenSocket(Socket):
    def __init__(self,factory,argv):
        super(PopenSocket,self).__init__(factory)
        self.argv=argv
        self.update_status()
    
    def create_socket(self):
        self.debug("Launching %s"%self.argv)
        self.p=subprocess.Popen(self.argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        self.socket=FileWrapper(self.p.stdout.fileno())

    def handle_read(self):
        try:
            data=self.socket.read(self.READ_CHUNK)
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
##
## Socket Factory.
## Methods:
## listen_tcp  - create new TCP listener
## connect_tcp - create new TCP connection
## run         - main event loop
##
class SocketFactory(object):
    def __init__(self, tick_callback=None, polling_method=None, controller=None):
        self.sockets={}     # fileno -> socket
        self.socket_name={} # socket -> name
        self.name_socket={} # name -> socket
        self.new_sockets=[] # list of (socket,name)
        self.tick_callback=tick_callback
        self.to_shutdown=False
        self.register_lock=RLock() # Guard for register/unregister operations
        self.controller=controller # Reference to controlling daemon
        self.get_active_sockets=None # Polling method
        self.setup_poller(polling_method)
        # Performance data
        self.cnt_polls=0 # Number of polls
    
    # Shutdown factory and exit next loop
    def shutdown(self):
        logging.info("Shutting down the factory")
        self.to_shutdown=True
    
    # Check select() available
    def has_select(self):
        return True
    
    # Check kevent/kqueue available
    def has_kevent(self):
        return False and hasattr(select, "kqueue")
    
    # Check poll() available
    def has_poll(self):
        return hasattr(select, "poll")
    
    # Check epoll() available
    def has_epoll(self):
        return hasattr(select, "epoll")

    ##
    ## Set up optimal polling function
    ##
    def setup_poller(self, polling_method=None):
        # Enable select()
        def setup_select_poller():
            logging.debug("Set up select() poller")
            self.get_active_sockets=self.get_active_select
            self.polling_method="select"
        
        # Enable poll()
        def setup_poll_poller():
            logging.debug("Set up poll() poller")
            self.get_active_sockets=self.get_active_poll
            self.polling_method="poll"
        
        # Enable epoll()
        def setup_epoll_poller():
            logging.debug("Set up epoll() poller")
            self.get_active_sockets=self.get_active_epoll
            self.polling_method="epoll"
        
        # Enable kevent/kqueue
        def setup_kevent_poller():
            logging.debug("Set up kevent/kqueue poller")
            self.get_active_sockets=self.get_active_kevent
            self.polling_method="kevent"
        
        if polling_method is None:
            # Read settings if available
            try:
                from noc.settings import config
                polling_method=config.get("main", "polling_method")
            except ImportError:
                polling_method="select"
        logging.debug("Setting up '%s' polling method"%polling_method)
        if polling_method=="optimal":
            # Detect possibilities
            if self.has_kevent(): # kevent
                setup_kevent_poller()
            elif self.has_epoll():
                setup_epoll_poller() # epoll
            elif self.has_poll(): # poll
                setup_poll_poller()
            else: # Fallback to select
                setup_select_poller()
        elif polling_method=="kevent" and self.has_kevent():
            setup_kevent_poller()
        elif polling_method=="epoll" and self.has_epoll():
            setup_epoll_poller()
        elif polling_method=="poll" and self.has_poll():
            setup_poll_poller()
        else:
            # Fallback to select
            setup_select_poller()
    
    ##
    ## Attack socket to the new_sockets list
    ##
    def register_socket(self,socket,name=None):
        logging.debug("register_socket(%s,%s)"%(socket,name))
        with self.register_lock:
            self.new_sockets+=[(socket,name)]
    
    ##
    ## Remove socket from factory
    ##
    def unregister_socket(self,socket):
        with self.register_lock:
            logging.debug("unregister_socket(%s)"%socket)
            if socket not in self.socket_name: # Not in factory yet
                return
            self.sockets.pop(socket.socket.fileno(),None)
            old_name=self.socket_name.pop(socket,None)
            self.name_socket.pop(old_name,None)
            if socket in self.new_sockets:
                self.new_sockets.remove(socket)
    
    ##
    ## Safe call of socket's method
    ## Returns call status (True/False)
    ##
    def guarded_socket_call(self,socket,method):
        try:
            method()
        except:
            exc=get_socket_error()
            try:
                if exc:
                    socket.on_error(exc)
                else:
                    socket.error("Unhandled exception when calling %s"%str(method))
                    error_report()
                    socket.close()
            except:
                socket.error("Error when handling error condition")
                error_report()
            return False
        return True
    
    ##
    ## Call socket's create_socket when necessary
    ## and add socket to the fabric
    ##
    def init_socket(self,socket,name):
        if not socket.socket_is_ready():
            socket.debug("Initializing socket")
            if not self.guarded_socket_call(socket,socket.create_socket):
                return
        if socket.socket is None:
            # Race condition raised. Socket is unregistered since last socket.create_socket call.
            # Silently ignore and exit
            return
        with self.register_lock:
            self.sockets[socket.socket.fileno()]=socket
            if socket in self.socket_name:
                # Socket was registred
                old_name=self.socket_name[socket]
                del self.socket_name[socket]
                if old_name:
                    del self.name_socket[old_name]
            self.socket_name[socket]=name
            if name:
                self.name_socket[name]=socket
        
    def listen_tcp(self, address, port, socket_class, backlog=100, nconnects=None, **kwargs):
        if not issubclass(socket_class,AcceptedTCPSocket):
            raise "socket_class should be a AcceptedTCPSocket subclass"
        l=ListenTCPSocket(self, address, port, socket_class, backlog, nconnects, **kwargs)
        l.set_name("listen-tcp-%s:%d"%(address,port))
        return l
    
    def connect_tcp(self,address,port,socket_class):
        if not issubclass(socket_class,ConnectedTCPSocket):
            raise "socket_class should be a ConnectedTCPSocket subclass"
        return socket_class(self,address,port)
        
    def get_socket_by_name(self,name):
        with self.register_lock:
            return self.name_socket[name]
        
    def get_name_by_socket(self,socket):
        with self.register_lock:
            return self.socket_name[socket]
    
    def __len__(self):
        with self.register_lock:
            return len(self.sockets)
        
    def close_stale(self):
        with self.register_lock:
            for s in [s for s in self.sockets.values() if s.is_stale()]:
                logging.debug("Closing stale socket %s"%s)
                s.close()
    ##
    ## Create pending sockets
    ##
    def create_pending_sockets(self):
        with self.register_lock:
            while self.new_sockets:
                socket,name=self.new_sockets.pop(0)
                self.init_socket(socket,name)
    
    ##
    ## Generic loop wrapper.
    ## Depends upon get_active_sockets() set up by constructor
    ##
    def loop(self, timeout=1):
        self.create_pending_sockets()
        if self.sockets:
            r, w=self.get_active_sockets(timeout)
            self.cnt_polls+=1
            #logging.debug("Active sockets: Read=%s Write=%s"%(repr(r), repr(w)))
            # Process write events before read to catch refused connections
            for fd in w:
                s=self.sockets.get(fd)
                if s:
                    self.guarded_socket_call(s, s.handle_write)
            # Process read events
            for fd in r:
                s=self.sockets.get(fd)
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
        # Get read and write candidates
        with self.register_lock:
            r=[f for f, s in self.sockets.items() if s.can_read()]
            w=[f for f, s in self.sockets.items() if s.can_write()]
        # Poll socket status
        try:
            r, w, x=select.select(r, w, [], timeout)
            return r, w
        except select.error, why:
            if why[0] not in (EINTR,):
                error_report() # non-ignorable errors
            return [], []
        except KeyboardInterrupt:
            logging.info("Got Ctrl+C, exiting")
            sys.exit(0)
        except:
            error_report()
            return [], []
    
    ##
    ## poll() implementation
    ##
    def get_active_poll(self, timeout):
        poll=select.poll()
        # Get read and write candidates
        with self.register_lock:
            for f, s in self.sockets.items():
                e=(select.POLLIN if s.can_read() else 0) | (select.POLLOUT if s.can_write() else 0)
                if e:
                    poll.register(f, e)
        # Poll socket status
        try:
            events=poll.poll(timeout*1000) # ms->s
        except select.error,why:
            if why[0] not in (EINTR,):
                error_report() # non-ignorable errors
            return [], []
        except:
            return [], []
        # Build result
        rset=[fd for fd, e in events if e&(select.POLLIN|select.POLLHUP)]
        wset=[fd for fd, e in events if e&select.POLLOUT]
        return rset, wset
    
    ##
    ## kevent/kqueue implementation
    ## (dumb one)
    ##
    def get_active_kevent(self, timeout):
        # Get read and write candidates
        kqueue=select.kqueue()
        events=[]
        with self.register_lock:
            for f, s in self.sockets.items():
                if s.can_write():
                    events+=[select.kevent(f, select.KQ_FILTER_WRITE, select.KQ_EV_ADD)]
                if s.can_read():
                    events+=[select.kevent(f, select.KQ_FILTER_READ, select.KQ_EV_ADD)]
        # Register events with kqueue
        kqueue.control(events, len(events), None)
        # Poll events
        rset=[]
        wset=[]
        for e in kqueue.control(None, len(events), timeout):
            if e.filter&select.KQ_FILTER_WRITE:
                wset+=[e.ident]
            if e.filter&select.KQ_FILTER_READ:
                rset+=[e.ident]
        return rset, wset
    
    ##
    ## poll() implementation
    ##
    def get_active_epoll(self, timeout):
        epoll=select.epoll()
        # Get read and write candidates
        with self.register_lock:
            for f, s in self.sockets.items():
                e=(select.EPOLLIN if s.can_read() else 0) | (select.EPOLLOUT if s.can_write() else 0)
                if e:
                    epoll.register(f, e)
        # Poll socket status
        try:
            events=epoll.poll(timeout)
        except select.error,why:
            if why[0] not in (EINTR,):
                error_report() # non-ignorable errors
            return [], []
        except:
            return [], []
        # Build result
        rset=[fd for fd, e in events if e&(select.EPOLLIN|select.EPOLLHUP)]
        wset=[fd for fd, e in events if e&select.EPOLLOUT]
        return rset, wset
    
    ##
    def run(self,run_forever=False):
        logging.debug("Running socket factory")
        self.create_pending_sockets()
        if run_forever:
            cond=lambda:True
        else:
            cond=lambda:len(self.sockets)>0
            # Wait for any socket
            while not cond():
                time.sleep(1)
        last_tick=time.time()
        last_stale=time.time()
        while cond() and not self.to_shutdown:
            self.loop(1)
            t=time.time()
            if self.tick_callback and t-last_tick>=1:
                try:
                    self.tick_callback()
                except:
                    error_report()
                    logging.info("Restoring from tick() failure")
                last_tick=t
            if t-last_stale>3:
                self.close_stale()
                last_stale=t
    
