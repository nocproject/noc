# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ActivatorStub
##     Activator replacement for ScriptTestCase
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nbsocket import SocketTimeoutError


class ActivatorStub(object):
    """
    Activator emulation using canned beef
    """
    TimeOutError = SocketTimeoutError

    def __init__(self, test):
        self.to_save_output = None
        self.servers = None
        self.factory = None
        self.log_cli_sessions = None
        self.test = test
        self.use_canned_session = True

    def on_script_exit(self, script):
        pass

    def cli(self, cmd):
        try:
            return self.test.cli[cmd]
        except KeyError:
            raise Exception("Command not found in canned session: %s" % cmd)

    def snmp_get(self, oid):
        try:
            return self.test.snmp_get[oid]
        except KeyError:
            raise self.TimeOutError()

    def snmp_getnext(self, oid):
        try:
            return self.test.snmp_getnext[oid]
        except KeyError:
            raise self.TimeOutError()

    def http_get(self, path):
        return self.test.http_get[path]

    def get_motd(self):
        return self.test.motd
