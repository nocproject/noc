# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP methods implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import tornado.ioloop
import tornado.gen
## NOC modules
from noc.core.ioloop.snmp import snmp_get, snmp_count
from noc.lib.snmp.error import SNMPError, TIMED_OUT
from noc.lib.log import PrefixLoggerAdapter


class SNMP(object):
    class TimeOutError(Exception):
        pass

    def __init__(self, script):
        self.script = script
        self.ioloop = None
        self.result = None
        self.logger = PrefixLoggerAdapter(script.logger, "snmp")

    def get_ioloop(self):
        if not self.ioloop:
            self.ioloop = tornado.ioloop.IOLoop()
        return self.ioloop

    def get(self, oids):
        """
        Perform SNMP GET request
        :param oid: string or list of oids
        :returns: eighter result scalar or dict of name -> value
        """
        @tornado.gen.coroutine
        def run():
            try:
                self.result = yield snmp_get(
                    address=self.script.credentials["address"],
                    oids=oids,
                    community=str(self.script.credentials["snmp_ro"]),
                    ioloop=self.get_ioloop()
                )
            except SNMPError, why:
                if why.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        self.get_ioloop().run_sync(run)
        return self.result

    def count(self, oid, filter=None):
        """
        Iterate MIB subtree and count matchinf instances
        :param oid: OID
        :param filter: Callable accepting oid and value and returning boolean
        """
        @tornado.gen.coroutine
        def run():
            try:
                self.result = yield snmp_count(
                    address=self.script.credentials["address"],
                    oid=oid,
                    bulk=self.script.has_snmp_bulk,
                    filter=filter,
                    ioloop=self.get_ioloop()
                )
            except SNMPError, why:
                if why.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        self.get_ioloop().run_sync(run)
        return self.result
