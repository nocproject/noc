# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.daemon import Daemon
from django.core.servers.fastcgi import runfastcgi

class FCGI(Daemon):
    daemon_name="noc-fcgi"
    def run(self):
        runfastcgi(["method=threaded", 
                    "daemonize=false",
                    "socket=%s"%self.config.get("fcgi","socket"),
                    "minspare=%d"%self.config.getint("fcgi","minspare"),
                    "maxspare=%d"%self.config.getint("fcgi","maxspare"),
                    "maxrequests=%s"%self.config.getint("fcgi","maxrequests"),
                    "maxchildren=%s"%self.config.getint("fcgi","maxchildren")])
