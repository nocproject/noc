##
## Clean and lightweight non-blocking socket I/O implementation
##
import socket,select,errno,time,logging,traceback
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, EINTR, EISCONN, ECONNREFUSED, EPIPE, errorcode

##
## Abstract non-blocking socket wrapper.
##
class Socket(object):
    def __init__(self,factory,sock):
        self.factory=factory
        self.socket=sock
        self.socket.setblocking(0)
        self.factory.register_socket(self)
    
    def __del__(self):
        logging.debug("Deallocating socket: %s"%self)
        
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
        logging.debug("%s:: %s"%(self,msg))
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
    
    def handle_read(self):
        s,addr=self.socket.accept()
        if self.factory.check_access(addr[0]):
            self.socket_class(self.factory,s)
        else:
            logging.error("Refusing connection from %s"%addr[0])
            s.close()

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
        
    def handle_write(self):
        sent=self.socket.send(self.out_buffer)
        self.out_buffer=self.out_buffer[sent:]
        
    def handle_connect(self):
        self.is_connected=True
        self.on_connect()
        
    def write(self,msg):
        self.debug("write(%s)"%msg)
        self.out_buffer+=msg
        
    def on_read(self,data): pass
    
    def on_connect(self): pass

##
## A socket wrapping accepted TCP connection.
## Following methods can be overrided for desired behavior:
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
    def __init__(self,factory,address,port):
        TCPSocket.__init__(self,factory,socket.socket(socket.AF_INET,socket.SOCK_STREAM))
        e=self.socket.connect_ex((address,port))
        if e in (0, EISCONN):
            self.handle_read()
            return
        elif e in (EINPROGRESS, EALREADY, EWOULDBLOCK):
            return
        else:
            raise socket.error, (e, errcode[e])
        
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
## Socket Factory.
## Methods:
## listen_tcp  - create new TCP listener
## connect_tcp - create new TCP connection
## run         - main event loop
##
class SocketFactory(object):
    def __init__(self):
        self.sockets={}
    
    def register_socket(self,socket):
        logging.debug("register_socket(%s)"%socket)
        self.sockets[socket.socket.fileno()]=socket
        
    def unregister_socket(self,socket):
        logging.debug("unregister_socket(%s)"%socket)
        del self.sockets[socket.socket.fileno()]
        
    def listen_tcp(self,address,port,socket_class):
        if not issubclass(socket_class,AcceptedTCPSocket):
            raise "socket_class should be a AcceptedTCPSocket subclass"
        ListenTCPSocket(self,address,port,socket_class)
    
    def connect_tcp(self,address,port,socket_class):
        if not issubclass(socket_class,ConnectedTCPSocket):
            raise "socket_class should be a ConnectedTCPSocket subclass"
        return socket_class(self,address,port)
        
    def check_access(self,address):
        return True
        
    def loop(self,timeout=1):
        if self.sockets:
            r=[f for f,s in self.sockets.items() if s.can_read()]
            w=[f for f,s in self.sockets.items() if s.can_write()]
            if r or w:
                r,w,x=select.select(r,w,[],timeout)
                if r or w:
                    # Write events processed before read events
                    # to catch connection refused causes
                    for f in w:
                        if f in self.sockets:
                            try:
                                self.sockets[f].handle_write()
                            except:
                                logging.error(traceback.format_exc())
                                self.sockets[f].close()
                    for f in r:
                        if f in self.sockets:
                            try:
                                self.sockets[f].handle_read()
                            except:
                                logging.error(traceback.format_exc())
                                self.sockets[f].close()
            else:
                time.sleep(timeout)
        else:
            time.sleep(timeout)
    
    def run(self):
        while self.sockets:
            self.loop()

if __name__=="__main__":
    test()