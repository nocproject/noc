# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HTTP Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.nbsocket import ConnectedTCPSocket
import noc.pm.probes
import urlparse,time
##
##
##
class HTTPProbeSocket(ConnectedTCPSocket):
    TTL=5
    def __init__(self,probe,address,port):
        self.probe=probe
        self.address=address
        self.port=port
        self.connect_time=None
        self.response_time=None
        url=self.probe.get("url","%s:%d"%(address,port))
        self.url=urlparse.urlparse(url)
        self.start_time=time.time()
        super(HTTPProbeSocket,self).__init__(probe.factory,address,port)
        
    def on_connect(self):
        self.connect_time=time.time()
        self.write("GET %(path)s HTTP/1.1\r\nHost: %(host)s\r\nConnection: close\r\nUser-Agent: %(uagent)s\r\nReferer: none\r\n\r\n"%{
            "path"   : self.url.path,
            "host"   : self.url.netloc,
            "uagent" : self.probe.get("user_agent","NOC SLA Monitor")
        })
        
    def on_close(self):
        self.response_time=time.time()
        if self.connect_time:
            self.probe.feed_result(self.address,{
                "status":True,
                "connect_time" : self.connect_time-self.start_time,
                "response_time": self.response_time-self.connect_time,
                "total_time"   : self.response_time-self.start_time})
        else:
            self.probe.feed_result(self.address,{"status":False})

    def on_read(self,data):
        pass
##
##
##
class HTTPProbe(noc.pm.probes.Probe):
    name="http"
    def run(self):
        for ip in [x.strip() for x in self.get("objects","").split(",")]:
            s=HTTPProbeSocket(self,ip,80)
