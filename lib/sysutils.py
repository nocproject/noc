# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various system utils
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import ConfigParser
import os
import signal


def get_daemon_config(daemon_name):
    """
    Read daemon config
    :param daemon_name:
    :return:
    """
    config = ConfigParser.SafeConfigParser()
    config.read("etc/%s.defaults" % daemon_name)
    config.read("etc/%s.conf" % daemon_name)
    return config


def refresh_config(daemon_name):
    """
    Gracefully sends SIGHUP to daemon
    :param daemon_name:
    :return:
    """
    config = get_daemon_config(daemon_name)
    # Read daemon PID from pidfile
    pidfile = config.get("main", "pidfile", None)
    if not pidfile:
        return
    try:
        with open(pidfile) as f:
            pid = int(f.read().strip())
    except:
        return
        # Try to send SIGHUP to daemon
    try:
        os.kill(pid, signal.SIGHUP)
    except:
        pass


def get_cpu_cores():
    """
    Return amount of available CPU cores
    :return: Number of CPU cores or 1
    :rtype: int
    """
    # Try to use Python 2.6+ multiprocessing
    try:
        import multiprocessing
        try:
            return multiprocessing.cpu_count()
        except NotImplementedError:
            pass
    except ImportError:
        pass
    # Try to use SC_NPROCESSORS_CONF
    try:
        return os.sysconf("SC_NPROCESSORS_CONF")
    except ValueError:
        return 1
