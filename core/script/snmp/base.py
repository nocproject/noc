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
from noc.core.ioloop.snmp import snmp_get, snmp_count, snmp_getnext
from noc.core.snmp.error import SNMPError, TIMED_OUT
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
        Iterate MIB subtree and count matching instances
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

    def getnext(self, oid, community_suffix=None,
                filter=None, cached=False, only_first=False):
        @tornado.gen.coroutine
        def run():
            try:
                self.result = yield snmp_getnext(
                    address=self.script.credentials["address"],
                    oid=oid,
                    bulk=self.script.has_snmp_bulk,
                    filter=filter,
                    only_first=only_first,
                    ioloop=self.get_ioloop()
                )
            except SNMPError, why:
                if why.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        self.get_ioloop().run_sync(run)
        return self.result

    def get_table(self, oid, community_suffix=None, cached=False):
        """
        GETNEXT wrapper. Returns a hash of <index> -> <value>
        """
        r = {}
        for o, v in self.getnext(oid, community_suffix=community_suffix,
                                 cached=cached):
            r[int(o.split(".")[-1])] = v
        return r

    def join_tables(self, oid1, oid2, community_suffix=None,
                    cached=False):
        """
        Generator returning a rows of two snmp tables joined by index
        """
        t1 = self.get_table(oid1, community_suffix=community_suffix,
                            cached=cached)
        t2 = self.get_table(oid2, community_suffix=community_suffix,
                            cached=cached)
        for k1, v1 in t1.items():
            try:
                yield (v1, t2[k1])
            except KeyError:
                pass

    def get_tables(self, oids, community_suffix=None, bulk=False,
                      min_index=None, max_index=None, cached=False):
        """
        Query list of SNMP tables referenced by oids and yields
        tuples of (key, value1, ..., valueN)

        :param oids: List of OIDs
        :param community_suffix: Optional suffix to be added to community
        :param bulk: Use BULKGETNEXT if true
        :param min_index:
        :param max_index:
        :param cached:
        :return:
        """
        def gen_table(oid):
            l = len(oid) + 1
            for o, v in self.getnext(oid, community_suffix=community_suffix,
                                     bulk=bulk, min_index=min_index,
                                     max_index=max_index, cached=cached):
                yield tuple([int(x) for x in o[l:].split(".")]), v

        # Retrieve tables
        tables = [dict(gen_table(oid)) for oid in oids]
        # Generate index
        index = set()
        for t in tables:
            index.update(t)
        # Yield result
        for i in sorted(index):
            yield [".".join([str(x) for x in i])] + [t.get(i) for t in tables]
