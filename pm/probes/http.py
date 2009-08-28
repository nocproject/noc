# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HTTP Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes.tcp import *
import re,urlparse,time
##
DEFAULT_PATH="/"
DEFAULT_USER_AGENT="NOC HTTP Probe"
##
## Send HTTP request and wait for 200 response
##
class HTTPProbeSocket(TCPProbeSocket):
    DEFAULT_PORT=80
    RESPONSE_RE=re.compile(r"^HTTP/1\.\d+ 200 OK")
    WAIT_UNTIL_CLOSE=True
    
    def get_request(self):
        return "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\nUser-Agent: %s\r\n\r\n"%(self.probe.url_path,self.service,self.probe.user_agent)
##
## HTTP server probe
##
## Probe accepts additional configuration parameters:
## port - port to connect to
## path - url's path part
## user_agent - User Agent string
class HTTPProbe(TCPProbe):
    name="http"
    socket_class=HTTPProbeSocket
    
    def __init__(self,daemon,probe_name,config):
        super(HTTPProbe,self).__init__(daemon,probe_name,config)
        self.user_agent=self.get("user_agent",DEFAULT_USER_AGENT)
        self.url_path=self.get("path",DEFAULT_PATH)
