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
        if ":" in service:
            address,port=service.split(":",1)
            port=int(port)
        else:
            address=service
            port=self.DEFAULT_PORT
        self.start_time=time.time()
        self.connect_time=None
        self.response_time=None
        self.data=""
        self.completed=False
        super(TCPProbeSocket,self).__init__(self.probe.factory,address,port)
    
    def on_connect(self):
        self.connect_time=time.time()
        request=self.get_request()
        if request:
            self.write(self.get_request())
    
    def on_read(self,data):
        self.data+=data
        if not self.completed and self.RESPONSE_RE:
            if self.RESPONSE_RE.search(self.data):
                self.completed=True
                self.response_time=time.time()
                if not self.WAIT_UNTIL_CLOSE:
                    self.close()
    
    def on_close(self):
        if not self.completed and self.WAIT_UNTIL_CLOSE and self.data:
            self.completed=True
            self.response_time=time.time()
        if self.completed:
            self.set_result(PR_OK,"OK")
        else:
            self.set_result(PR_FAIL,"Failure")
        self.set_data("connect_time", self.connect_time-self.start_time if self.connect_time else None)
        self.set_data("response_time", self.response_time-self.connect_time if self.connect_time and self.response_time else None)
        self.probe.on_close(self.service)
        
    def get_request(self):
        return self.REQUEST

    def set_data(self,param,value):
        self.probe.set_data(self.service,param,value)

    def set_result(self,result,message="OK"):
        self.probe.set_result(self.service,result,message)
##
## TCP probe
## * Connects to the service
## * Sends request (optional)
## * Watch for response
##
class TCPProbe(Probe):
    name=None # Abstract probe
    socket_class=TCPProbeSocket
    parameters = {
        "connect_time" : {},
        "response_time": {},
    }
    def __init__(self,daemon,probe_name,config):
        self.sockets={} # Service -> socket
        super(TCPProbe,self).__init__(daemon,probe_name,config)

    def on_start(self):
        for service in self.services:
            self.sockets[service]=self.socket_class(self,service)

    def on_stop(self):
        for service,sock in self.sockets.items():
            sock.set_result(PR_FAIL,"Timeout expired")
            sock.close()

    def on_close(self,service):
        del self.sockets[service]
        if len(self.sockets)==0:
            self.exit()
