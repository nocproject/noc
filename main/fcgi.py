# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-fcgi daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.daemon import Daemon
from django.core.handlers.wsgi import WSGIHandler
from flup.server.fcgi import WSGIServer

class FCGI(Daemon):
    daemon_name="noc-fcgi"
    def run(self):
        wsgi_opts={
            "minSpare"   : int(self.config.getint("fcgi","minspare")),
            "maxSpare"   : int(self.config.getint("fcgi","maxspare")),
            "maxThreads" : self.config.getint("fcgi","maxchildren"),
            "debug"      : False, # turn off flup tracebacks
            "bindAddress": self.config.get("fcgi","socket"),
            "umask"      : 0, # Emulate BSD behavior on linux
        }
        WSGIServer(WSGIHandler(), **wsgi_opts).run()
