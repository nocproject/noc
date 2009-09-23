# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FPing Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes.popen import *
from noc.lib.nbsocket import PopenSocket

##
## Returns:
##     min_delay, max_delay, avg_delay, packet_loss, jitter
##
class FPingProbeSocket(PopenProbeSocket):
    def get_cmd(self):
        return [self.probe.fping_path,"-q","-b",str(self.probe.packet_size-28),"-C",str(self.probe.num_requests)]+self.probe.s_list
    ##
    ## Parse self.data
    ##
    def on_close(self):
        for l in self.data.split("\n"):
            l=l.strip()
            if ":" not in l or "duplicate for" in l:
                continue
            s,r=l.split(":")
            s=s.strip()
            r=[x.strip() for x in r.split()]
            # Process service data
            cr=[float(x) for x in r if x!="-"]
            self.probe.set_data(s,"loss",float(len(r)-len(cr))/len(r))
            if cr:
                self.probe.set_data(s,"min_delay", min(cr))
                self.probe.set_data(s,"max_delay", max(cr))
                self.probe.set_data(s,"avg_delay", reduce(lambda x,y:x+y,cr,0)/len(cr))
                self.probe.set_data(s,"jitter"   , self.jitter(cr))
            else:
                self.probe.set_data(s,"min_delay", None)
                self.probe.set_data(s,"max_delay", None)
                self.probe.set_data(s,"avg_delay", None)
                self.probe.set_data(s,"jitter",    None)
        super(FPingProbeSocket,self).on_close()
    ##
    ## Calculate jitter (See RFC1889)
    ##
    def jitter(self,rtts):
        transit=reduce(lambda x,y:x+y,rtts,0)/len(rtts) # Average delay
        s_jitter=0.0
        s_transit=rtts[0]
        for transit in rtts[1:]:
            d=transit-s_transit
            s_transit=transit
            if d<0:
                d=-d
            s_jitter+=(d-s_jitter)/16.0
        return s_jitter
##
## FPing Probe
## * Executes fping command and parses output
##
class FPingProbe(PopenProbe):
    name="fping"
    socket_class=FPingProbeSocket # Socket class performing checking
    parameters = {
        "min_delay" : {},
        "avg_delay" : {},
        "max_delay" : {},
        "loss"      : {},
        "jitter"    : {},
    }
    def __init__(self,daemon,probe_name,config):
        self.fping_path=daemon.config.get("path","fping")
        super(FPingProbe,self).__init__(daemon,probe_name,config)
        self.num_requests=self.getint("num_requests",5)
        self.packet_size=self.getint("packet_size",64)
        self.s_list=self.services[:]
        self.services=["X"]
        
