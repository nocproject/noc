# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-launcher daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.lib.daemon import Daemon
import time,subprocess,sys,os,logging,stat,ConfigParser

##
## Daemon wrapper
##
class DaemonData(object):
    def __init__(self,name,enabled):
        self.name=name
        self.enabled=enabled
        self.pid=None
        self.pidfile=None
    
    def __repr__(self):
        return "<DaemonData %s>"%self.name
    ##
    ## Get pidfile path from daemon config
    ##
    def get_pidfile(self):
        config=ConfigParser.SafeConfigParser()
        config.read("etc/%s.defaults"%self.name)
        config.read("etc/%s.conf"%self.name)
        return config.get("main","pidfile")
        
    ##
    ## Launch daemon
    ##
    def launch(self):
        logging.info("Launching %s"%self.name)
        pid=os.fork()
        if pid:
            self.pid=pid
            logging.info("Daemon %s started as PID %d"%(self.name,self.pid))
        else:
            # Run child
            os.execv(sys.executable,[sys.executable,"./scripts/%s.py"%self.name,"launch"])

class Launcher(Daemon):
    daemon_name="noc-launcher"
    def __init__(self):
        super(Launcher,self).__init__()
        self.daemons=[]
        for n in ["fcgi","sae","activator","classifier","correlator"]:
            dn="noc-%s"%n
            is_enabled=self.config.getboolean(dn,"enabled")
            self.daemons+=[DaemonData(dn,is_enabled)]
        
    def run(self):
        while True:
            for d in self.daemons:
                if not d.enabled: # Skip disabled daemons
                    continue
                if d.pid is None: # Launch required daemons
                    d.launch()
                else: # Check daemon status
                    try:
                        pid,status=os.waitpid(d.pid,os.WNOHANG)
                    except OSError:
                        pid=0
                        status=0
                    if pid==d.pid:
                        logging.info("%s daemon is terminated with status %d"%(d.name,d.pid))
                        d.pid=None
            time.sleep(1)
