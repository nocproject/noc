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
## Send HTTP request and wait for 200 response
##
class HTTPProbeSocket(TCPProbeSocket):
    DEFAULT_PORT=80
    RESPONSE_RE=re.compile(r"^HTTP/1\.\d+ 200 OK")
    WAIT_UNTIL_CLOSE=True
    
    def get_request(self):
        return "GET / HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n"%self.service
##
## HTTP server probe
##
class HTTPProbe(TCPProbe):
    name="http"
    socket_class=HTTPProbeSocket
