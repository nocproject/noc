# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SSH provider
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.lib.nbsocket import PTYSocket
from noc.sa.script.cli import CLI
from noc.settings import config

##
##
##
class CLISSHSocket(CLI, PTYSocket):
    TTL=30
    def __init__(self,factory,profile,access_profile):
        logging.debug("CLISSHSocket connecting '%s'"%access_profile.address)
        cmd_args=[config.get("path","ssh"),
            "-o","StrictHostKeyChecking=no",
            "-o","UserKnownHostsFile=/dev/null",
            "-o","ConnectTimeout=15",
            "-l",access_profile.user]
        if access_profile.port and access_profile.port!=22:
            cmd_args+=["-p",str(access_profile.port)]
        self._log_label="SSH: %s"%access_profile.address
        cmd_args+=[access_profile.address]
        CLI.__init__(self,profile,access_profile)
        PTYSocket.__init__(self,factory,cmd_args)
    
    def is_stale(self):
        self.async_check_fsm()
        return PTYSocket.is_stale(self)
    
    def log_label(self):
        return self._log_label
    
    def debug(self,msg):
        logging.debug("[%s] %s"%(self.log_label(),msg))
    

