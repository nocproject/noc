# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Clean and lightweight non-blocking socket I/O implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import socket,select,errno,time,logging,pty,os,signal
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, EINTR, EISCONN, ECONNREFUSED, EPIPE, errorcode
from noc.lib.debug import error_report

##
## Abstract non-blocking socket wrapper.
##
class Socket(object):
    TTL=None # maximum time to live in seconds
    def __init__(self,factory,sock):
        self.factory=factory
        self.socket=sock
        self.socket.setblocking(0)
        self.factory.register_socket(self)
        self.name=None
        self.start_time=time.time()
    
    def __del__(self):
        self.debug("Deallocating")
        
    def can_read(self):
        return True
        
    def can_write(self):
        return True
        
    def handle_read(self):
        pass
        
    def handle_write(self):
        pass
        
    def on_close(self):
        pass
        
    def close(self):
        if self.socket:
            self.factory.unregister_socket(self)
            self.socket.close()
            self.socket=None
            self.on_close()
    
    def debug(self,msg):
        logging.debug("[%s(0x%x)] %s"%(self.__class__.__name__,id(self),msg))
    
    def set_name(self,name):
        self.name=name
        self.factory.register_socket(self,name)
    # Stale sockets detection.
    # Called by SocketFactory.close_stale to determine should socket be closed forcefully
    def is_stale(self):
        return self.TTL and time.time()-self.start_time>=self.TTL
##
## Abstract Protocol Parser.
## Accepts data via feed method, polupates internal buffer (self.in_buffer).
## and calls parse_pdu.
## parse_pdu must parse self.in_buffer, retrieve all complete pdu,
## remove them from buffer and return a list of parsed PDU (or empty list if not found)
## All parsed pdu are returned via callback method
class Protocol(object):
    def __init__(self,callback):
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
    def __init__(self,factory,address,port,socket_class):
        Socket.__init__(self,factory,socket.socket(socket.AF_INET,socket.SOCK_STREAM))
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,
            self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR) | 1)
        self.socket.bind((address,port))
        self.socket.listen(5)
        self.socket_class=socket_class
        self.address=address
        self.port=port
    
    def handle_read(self):
        s,addr=self.socket.accept()
        if self.socket_class.check_access(addr[0]):
            self.socket_class(self.factory,s)
        else:
            logging.error("Refusing connection from %s"%addr[0])
            s.close()
##
## UDP Listener
## Waits for UDP packets on specified ports
## and calls on_read for each packet
class ListenUDPSocket(Socket):
    def __init__(self,factory,address,port):
        Socket.__init__(self,factory,socket.socket(socket.AF_INET,socket.SOCK_DGRAM))
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,
            self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR) | 1)
        self.socket.bind((address,port))
    
    def handle_read(self):
        msg,transport_address=self.socket.recvfrom(8192)
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
    def __init__(self,factory,socket):
        Socket.__init__(self,factory,socket)
        self.is_connected=False
        self.out_buffer=""
        if self.protocol_class:
            self.protocol=self.protocol_class(self.on_read)
        self.in_shutdown=False
        
    def close(self,flush=False):
        if flush and len(self.out_buffer)>0:
            self.in_shutdown=True
        else:
            super(TCPSocket,self).close()
        
    def handle_write(self):
        sent=self.socket.send(self.out_buffer)
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
        TCPSocket.__init__(self,factory,socket)
        self.handle_connect()
    
    @classmethod
    def check_access(cls,address):
        return True
        
    def handle_read(self):
        try:
            data=self.socket.recv(8192)
        except socket.error,why:
            if why[0] in (ECONNRESET,ENOTCONN,ESHUTDOWN):
                self.close()
                return
            raise socket.error, why
        if data=="":
            self.close()
            return
        if self.protocol_class:
            self.protocol.feed(data)
        else:
            self.on_read(data)
        
    def can_write(self):
        return self.out_buffer
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
    def __init__(self,factory,address,port,local_address=None):
        TCPSocket.__init__(self,factory,socket.socket(socket.AF_INET,socket.SOCK_STREAM))
        if local_address:
            self.socket.bind((local_address,0))
        e=self.socket.connect_ex((address,port))
        if e in (0, EISCONN):
            #self.handle_read()
            return
        elif e in (EINPROGRESS, EALREADY, EWOULDBLOCK):
            return
        else:
            raise socket.error, (e, errorcode[e])
        
    def handle_read(self):
        if not self.is_connected:
            self.handle_connect()
            return
        try:
            data=self.socket.recv(8192)
        except socket.error,why:
            if why[0]==ECONNREFUSED:
                self.on_conn_refused()
                self.close()
                return
            if why[0] in (ECONNRESET,ENOTCONN,ESHUTDOWN):
                self.close()
                return
            raise socket.error,why
        if not data:
            self.close()
            return
        if self.protocol_class:
            self.protocol.feed(data)
        else:
            self.on_read(data)
    
    def can_write(self):
        return self.out_buffer or not self.is_connected
    
    def handle_write(self):
        if not self.is_connected:
            try:
                self.socket.send("")
            except socket.error,why:
                if why[0]==EPIPE:
                    self.on_conn_refused()
                    self.close()
                    return
                raise socket.error,why
            self.handle_connect()
            return
        TCPSocket.handle_write(self)
    
    def on_conn_refused(self): pass
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
        
    def setblocking(self,status):
        pass
##
## PTY Socket Emulation
## Events: on_read, on_close
##
class PTYSocket(Socket):
    def __init__(self,factory,argv):
        self.out_buffer=""
        self.pid,fd=pty.fork()
        if self.pid==0:
            os.execv(argv[0],argv)
        else:
            Socket.__init__(self,factory,FileWrapper(fd))
            
    def handle_read(self):
        try:
            data=self.socket.read(8192)
        except OSError:
            self.close()
            return
        if data:
            self.on_read(data)
        else:
            self.close()

    def can_write(self):
        return self.out_buffer
        
    def handle_write(self):
        sent=self.socket.send(self.out_buffer)
        self.out_buffer=self.out_buffer[sent:]

    def handle_connect(self):
        self.is_connected=True
        self.on_connect()

    def write(self,msg):
        self.debug("write(%s)"%repr(msg))
        self.out_buffer+=msg
    
    def close(self):
        Socket.close(self)
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
## Socket Factory.
## Methods:
## listen_tcp  - create new TCP listener
## connect_tcp - create new TCP connection
## run         - main event loop
##
class SocketFactory(object):
    def __init__(self,tick_callback=None):
        self.sockets={}
        self.socket_name={}
        self.name_socket={}
        self.tick_callback=tick_callback
    
    def register_socket(self,socket,name=None):
        logging.debug("register_socket(%s,%s)"%(socket,name))
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
        
    def unregister_socket(self,socket):
        logging.debug("unregister_socket(%s)"%socket)
        del self.sockets[socket.socket.fileno()]
        old_name=self.socket_name[socket]
        del self.socket_name[socket]
        if old_name:
            del self.name_socket[old_name]
        
    def listen_tcp(self,address,port,socket_class):
        if not issubclass(socket_class,AcceptedTCPSocket):
            raise "socket_class should be a AcceptedTCPSocket subclass"
        l=ListenTCPSocket(self,address,port,socket_class)
        l.set_name("listen-tcp-%s:%d"%(address,port))
        return l
    
    def connect_tcp(self,address,port,socket_class):
        if not issubclass(socket_class,ConnectedTCPSocket):
            raise "socket_class should be a ConnectedTCPSocket subclass"
        return socket_class(self,address,port)
        
    def get_socket_by_name(self,name):
        return self.name_socket[name]
        
    def get_name_by_socket(self,socket):
        return self.socket_name[socket]
    
    def __len__(self):
        return len(self.sockets)
        
    def close_stale(self):
        for s in [s for s in self.sockets.values() if s.is_stale()]:
            logging.debug("Closing stale socket %s"%s)
            s.close()
        
    def loop(self,timeout=1):
        if self.sockets:
            r=[f for f,s in self.sockets.items() if s.can_read()]
            w=[f for f,s in self.sockets.items() if s.can_write()]
            if r or w:
                try:
                    r,w,x=select.select(r,w,[],timeout)
                except select.error,why:
                    if why[0]==EINTR:
                        return
                    raise
                if r or w:
                    # Write events processed before read events
                    # to catch connection refused causes
                    for f in w:
                        if f in self.sockets:
                            try:
                                self.sockets[f].handle_write()
                            except:
                                error_report()
                                try:
                                    self.sockets[f].close()
                                except:
                                    pass
                    for f in r:
                        if f in self.sockets:
                            try:
                                self.sockets[f].handle_read()
                            except:
                                error_report()
                                try:
                                    self.sockets[f].close()
                                except:
                                    pass
            else:
                time.sleep(timeout)
        else:
            time.sleep(timeout)
    
    def run(self,run_forever=False):
        if run_forever:
            cond=lambda:True
        else:
            cond=lambda:len(self.sockets)>0
            # Wait for any socket
            while not cond():
                time.sleep(1)
        last_tick=time.time()
        last_stale=time.time()
        while cond():
            self.loop(1)
            t=time.time()
            if self.tick_callback and t-last_tick>=1:
                self.tick_callback()
                last_tick=t
            if t-last_stale>10:
                self.close_stale()
                last_stale=t
    
    ##
    ## Return amount of active sockets which are descendants from sclass
    ##
    def count_subclass_sockets(self,sclass):
        return len([s for s in self.sockets.values() if issubclass(s.__class__,sclass)])
