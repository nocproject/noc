# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Process Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes.popen import *
from noc.lib.nbsocket import PopenSocket
import time,logging,os

##
## Returns:
##     VSIZE, RSS
##
class ProcessProbeSocket(PopenProbeSocket):
    def get_cmd(self):
        return getattr(self,"get_cmd_%s"%self.probe.uname)()
    ## MAC OS X
    def get_cmd_darwin(self):
        return ["/bin/ps","-ax","-o","rss,vsize,command"]
    ## Linux
    def get_cmd_linux(self):
        return ["/bin/ps","-ax","-o","rss,vsize,cmd"]
    ## Solaris
    def get_cmd_sunos(self):
        return ["/bin/ps","-e","-o","rss,vsz,args"]
    ## FreeBSD
    def get_cmd_freebsd(self):
        return ["/bin/ps","-ax","-o","rss,vsz,command"]
    ## 
    ##
    ## Parse self.data
    ##
    def on_close(self):
        for l in self.data.split("\n")[1:]:
            l=l.strip()
            if not l:
                continue
            rss,vsize,command=l.split(None,2)
            for ps in self.probe.watch_processes:
                if ps in command:
                    rss=int(rss)*1024
                    vsize=int(vsize)*1024
                    self.set_data(ps+"_VSIZE",vsize)
                    self.set_data(ps+"_RSS",rss)
                    break
        super(ProcessProbeSocket,self).on_close()
##
## Popen Probe
## * Executes ps command and parses output
##
class ProcessProbe(PopenProbe):
    name="process"
    socket_class=ProcessProbeSocket # Socket class performing checking
    processes=[]
    def __init__(self,daemon,probe_name,config):
        self.uname=os.uname()[0].lower()
        super(ProcessProbe,self).__init__(daemon,probe_name,config)
        self.watch_processes=set(self.processes+self.expand_config_list("processes"))
        self.expand_parameters()
    #
    def delay_parameter_expansion(self):
        return True
    ##
    def expand_parameters(self):
        super(ProcessProbe,self).expand_parameters()
        for ps in self.watch_processes:
            for service in self.services:
                self.expand_parameter(service,ps+"_VSIZE",{})
                self.expand_parameter(service,ps+"_RSS",{})
