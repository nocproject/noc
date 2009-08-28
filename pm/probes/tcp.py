# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes import *
from noc.lib.nbsocket import ConnectedTCPSocket
import time,logging

##
## Abstract TCP service wrapper
##
class TCPProbeSocket(ConnectedTCPSocket):
    DEFAULT_PORT=0     # Default service port
    REQUEST=""         # Request to send after connect. Empty string means do not send request
    RESPONSE_RE=None   # Reqular expression to match response
    WAIT_UNTIL_CLOSE=False # True - wait until server close the socket
    def __init__(self,probe,service):
        self.probe=probe
        self.service=service
        port=self.probe.getint("port",self.DEFAULT_PORT)
        self.start_time=time.time()
        self.connect_time=None
        self.response_time=None
        self.data=""
        self.completed=False
        super(TCPProbeSocket,self).__init__(self.probe.factory,service,port)
    ##
    ## Send request if get_request() returns result
    ##
    def on_connect(self):
        self.connect_time=time.time()
        request=self.get_request()
        if request:
            self.write(self.get_request())
    ##
    ## Match received data againse RESPONSE_RE
    ## close socket immediately if WAIT_UNTIL_CLOSE==False and RESPONSE_RE matches
    ##
    def on_read(self,data):
        self.data+=data
        if not self.completed and self.RESPONSE_RE:
            if self.RESPONSE_RE.search(self.data):
                self.completed=True
                self.response_time=time.time()
                if not self.WAIT_UNTIL_CLOSE:
                    self.close()
    ##
    ## Calculate parameters and notify the probe
    ##
    def on_close(self):
        if not self.completed and self.WAIT_UNTIL_CLOSE and self.data:
            self.completed=True
            self.response_time=time.time()
        if self.completed:
            self.set_result(PR_OK,"OK")
        else:
            self.set_result(PR_FAIL,"Failure")
        self.set_data("connect_delay", self.connect_time-self.start_time if self.connect_time else None)
        self.set_data("response_delay", self.response_time-self.connect_time if self.connect_time and self.response_time else None)
        if self.WAIT_UNTIL_CLOSE:
            self.set_data("response_size", len(self.data))
        self.probe.on_close(self.service)
    ##
    ## Returns request to be send on connect
    ##
    def get_request(self):
        return self.REQUEST
    ##
    ## Notify probe about parameter value
    ##
    def set_data(self,param,value):
        self.probe.set_data(self.service,param,value)
    ##
    ## Notify probe about result
    ##
    def set_result(self,result,message="OK"):
        self.probe.set_result(self.service,result,message)
##
## TCP probe
## * Connects to the service
## * Sends request (if socket_class.get_request() returns value)
## * Watches for response and matches socket_class.RESPONSE_RE
## * When socket_class.WAIT_UNTIL_CLOSE set wait ontil remote end close connection
##
## Probe accepts additional configuration options
## port - TCP port to connect to
##
class TCPProbe(Probe):
    name=None # Abstract probe
    socket_class=TCPProbeSocket # Socket class performing checking
    parameters = {
        "connect_delay"  : {}, # TCP Three-way handshake delay (in seconds)
        "response_delay" : {}, # Delay between connection estabilishment and receiving of the reply (in seconds)
        "response_size"  : {}, # Size of response (in octets). Generated only when WAIT_UNTIL_CLOSE==True
    }
    def __init__(self,daemon,probe_name,config):
        self.sockets={} # Service -> socket
        super(TCPProbe,self).__init__(daemon,probe_name,config)
    ##
    ## Create checking socket for each service
    ##
    def on_start(self):
        for service in self.services:
            self.sockets[service]=self.socket_class(self,service)
    ##
    ## Close still open sockets
    ##
    def on_stop(self):
        for service,sock in self.sockets.items():
            sock.set_result(PR_FAIL,"Timeout expired")
            sock.close()
    ##
    ## Called by socket to indicate socket closing
    ##
    def on_close(self,service):
        del self.sockets[service]
        if len(self.sockets)==0:
            self.exit()
