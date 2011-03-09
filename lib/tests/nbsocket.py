# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## lib/nbsocket tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Python modules
from unittest import TestCase
## NOC modules
from noc.lib.nbsocket import *

##
## TCP Ping server
##
class TCPServer(AcceptedTCPSocket):
    def on_read(self, data):
        if data=="PING":
            self.write("PONG")
            self.factory.tcp_server_success+=1
    

##
## TCP Ping client
##
class TCPClient(ConnectedTCPSocket):
    def on_connect(self):
        self.write("PING")
    
    def on_read(self, data):
        if data=="PONG":
            self.factory.tcp_client_success+=1
        self.close()
    
##
##
##
class PopenTestSocket(PopenSocket):
    def on_read(self, data):
        if data:
            self.factory.popen_success+=1
    

##
##
##
class PTYTestSocket(PopenSocket):
    def on_read(self, data):
        if data:
            self.factory.pty_success+=1

##
## NonBlocking sockets tests
##
class NBSocketTestCase(TestCase):
    TCP_CLIENTS=200
    IPv4_ADDRESS="127.0.0.1"
    TCP_PORT=65028
    POPEN_CMD=["/bin/ls","/"]
    
    ## Prepare test sockets
    def set_up_sockets(self, factory, port):
        # Initialize counters
        factory.tcp_server_success=0
        factory.tcp_client_success=0
        factory.popen_success=0
        factory.pty_success=0
        # Create listeners
        factory.listen_tcp(self.IPv4_ADDRESS, port, TCPServer, nconnects=self.TCP_CLIENTS)
        # Create TCP clients
        for i in range(self.TCP_CLIENTS):
            TCPClient(factory, self.IPv4_ADDRESS, port)
        # Create popen socket
        PopenTestSocket(factory, self.POPEN_CMD)
        # Create PTY socket
        PTYTestSocket(factory, self.POPEN_CMD)
    
    ## Validate result
    def check_result(self, factory):
        self.assertEquals(factory.tcp_server_success, self.TCP_CLIENTS)
        self.assertEquals(factory.tcp_client_success, self.TCP_CLIENTS)
        self.assertEquals(factory.popen_success, 1)
        self.assertEquals(factory.pty_success, 1)
    
    ## Poller test wrapper
    def poller_test(self, polling_method, port):
        factory=SocketFactory(polling_method=polling_method)
        if factory.polling_method!=polling_method:
            return
        self.set_up_sockets(factory, port)
        factory.run()
        self.check_result(factory)
    
    ## Test select() method
    def test_select(self):
        self.poller_test("select", self.TCP_PORT)
    
    ## Test poll method
    def test_poll(self):
        self.poller_test("poll", self.TCP_PORT+1)
    
    ## Test kevent/kqueue method
    def test_kevent(self):
        self.poller_test("kevent", self.TCP_PORT+2)
    
    ## Test kevent/kqueue method
    def test_epoll(self):
        self.poller_test("epoll", self.TCP_PORT+3)
    
