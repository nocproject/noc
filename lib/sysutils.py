# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various system utils
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import ConfigParser,os,signal
##
## Read daemon config
##
def get_daemon_config(daemon_name):
    config=ConfigParser.SafeConfigParser()
    config.read("etc/%s.defaults"%daemon_name)
    config.read("etc/%s.conf"%daemon_name)
    return config
##
## Gracefully sends SIGHUP to daemon
##
def refresh_config(daemon_name):
    config=get_daemon_config(daemon_name)
    # Read daemon PID from pidfile
    pidfile=config.get("main","pidfile",None)
    if not pidfile:
        return
    try:
        with open(pidfile) as f:
            pid=int(f.read().strip())
    except:
        return
    # Try to send SIGHUP to daemon
    try:
        os.kill(pid,signal.SIGHUP)
    except:
        pass
