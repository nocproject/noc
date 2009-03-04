# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SLA Monitor
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.daemon import Daemon
from noc.lib.nbsocket import SocketFactory
import logging,time
from noc.pm.probes import probe_registry

probe_registry.register_all()

##
## SLA Monitor Daemon
##
class SLAMonitor(Daemon):
    daemon_name="noc-sla"
    ##
    ##
    ##
    def __init__(self):
        Daemon.__init__(self)
        logging.info("Running SLA Monitor")
        self.factory=SocketFactory()
        self.probes={}
        self.init_probes()
    ##
    ##
    ##
    def init_probes(self):
        for probe_name in self.config.sections():
            if probe_name=="main":
                continue
            probe=self.config.get(probe_name,"probe")
            if not probe:
                self.error("No probe type specified for '%s'"%probe_name)
                continue
            if probe not in probe_registry.classes:
                self.error("Invalid probe type '%s' for probe '%s'"%(probe,probe_name))
                continue
            probe=probe_registry[probe]
            self.probes[probe_name]=probe(probe_name,self,self.config)
            self.probes[probe_name].run()
    ##
    ##
    ##
    def run(self):
        while True:
            self.factory.run()
            print "."
