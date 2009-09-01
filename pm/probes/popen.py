# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Popen Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes import *
from noc.lib.nbsocket import PopenSocket
import time,logging

##
##
##
class PopenProbeSocket(PopenSocket):
    CMD=None
    def __init__(self,probe,service):
        self.service=service
        self.data=""
        self.probe=probe
        super(PopenProbeSocket,self).__init__(probe.factory,self.get_cmd())
    
    def get_cmd(self):
        return self.CMD
    
    def on_read(self,data):
        self.data+=data
    ##
    ## Parse self.data
    ##
    def on_close(self):
        self.probe.on_close(self.service)

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
## Popen Probe
## * Executes command and parses output
##
##
class PopenProbe(Probe):
    name=None # Abstract probe
    socket_class=PopenProbeSocket # Socket class performing checking
    parameters = {
    }
    def __init__(self,daemon,probe_name,config):
        self.sockets={} # Service -> socket
        super(PopenProbe,self).__init__(daemon,probe_name,config)
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
