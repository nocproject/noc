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
from noc.core.ioloop.snmp import (snmp_get, snmp_count, snmp_getnext,
                                  snmp_set)
from noc.core.snmp.error import SNMPError, TIMED_OUT
from noc.core.snmp.version import SNMP_v1, SNMP_v2c, SNMP_v3
from noc.lib.log import PrefixLoggerAdapter


class SNMP(object):
    class TimeOutError(Exception):
        pass

    def __init__(self, script, beef=None):
        self.script = script
        self.ioloop = None
        self.result = None
        self.beef = beef
        self.logger = PrefixLoggerAdapter(script.logger, "snmp")

    def close(self):
        if self.ioloop:
            self.logger.debug("Closing IOLoop")
            self.ioloop.close(all_fds=True)
            self.ioloop = None

    def get_ioloop(self):
        if not self.ioloop:
            self.logger.debug("Creating IOLoop")
            self.ioloop = tornado.ioloop.IOLoop()
        return self.ioloop

    def _get_snmp_version(self, version=None):
        if version:
            return version
        if self.script.has_snmp_v2c():
            return SNMP_v2c
        elif self.script.has_snmp_v3():
            return SNMP_v3
        elif self.script.has_snmp_v1():
            return SNMP_v1
        return SNMP_v2c

    def get(self, oids, cached=False, version=None):
        """
        Perform SNMP GET request
        :param oid: string or list of oids
        :param cached: True if get results can be cached during session
        :returns: eigther result scalar or dict of name -> value
        """
        @tornado.gen.coroutine
        def run():
            try:
                self.result = yield snmp_get(
                    address=self.script.credentials["address"],
                    oids=oids,
                    community=str(self.script.credentials["snmp_ro"]),
                    tos=self.script.tos,
                    ioloop=self.get_ioloop(),
                    version=version
                )
                if self.beef:
                    # Restore from beef
                    self.beef.set_snmp_get(oids, self.result)
            except SNMPError as e:
                if e.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        version = self._get_snmp_version(version)
        self.get_ioloop().run_sync(run)
        return self.result

    def set(self, *args):
        """
        Perform SNMP GET request
        :param oid: string or list of oids
        :returns: eigther result scalar or dict of name -> value
        """
        @tornado.gen.coroutine
        def run():
            try:
                self.result = yield snmp_set(
                    address=self.script.credentials["address"],
                    varbinds=varbinds,
                    community=str(self.script.credentials["snmp_rw"]),
                    tos=self.script.tos,
                    ioloop=self.get_ioloop()
                )
            except SNMPError as e:
                if e.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        if len(args) == 1:
            varbinds = args
        elif len(args) == 2:
            varbinds = [(args[0], args[1])]
        else:
            raise ValueError("Invalid varbinds")
        self.get_ioloop().run_sync(run)
        return self.result

    def count(self, oid, filter=None, version=None):
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
                    community=str(self.script.credentials["snmp_ro"]),
                    bulk=self.script.has_snmp_bulk,
                    filter=filter,
                    tos=self.script.tos,
                    ioloop=self.get_ioloop(),
                    version=version
                )
            except SNMPError as e:
                if e.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        version = self._get_snmp_version(version)
        self.get_ioloop().run_sync(run)
        return self.result

    def getnext(self, oid, community_suffix=None,
                filter=None, cached=False,
                only_first=False, bulk=None,
                max_repetitions=None, version=None):
        @tornado.gen.coroutine
        def run():
            try:
                self.result = yield snmp_getnext(
                    address=self.script.credentials["address"],
                    oid=oid,
                    community=str(self.script.credentials["snmp_ro"]),
                    bulk=self.script.has_snmp_bulk if bulk is None else bulk,
                    max_repetitions=max_repetitions,
                    filter=filter,
                    only_first=only_first,
                    tos=self.script.tos,
                    ioloop=self.get_ioloop(),
                    version=version
                )
            except SNMPError as e:
                if e.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        version = self._get_snmp_version(version)
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
                                     cached=cached):
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

    def join(self, oids, community_suffix=None, cached=False, join="left"):
        """
        Query list of tables, merge by oid index
        Tables are records of:
        * <oid>.<index> = value

        join may be one of:
        * left
        * inner
        * outer

        Yield records of (<index>, <value1>, ..., <valueN>)
        """
        tables = [
            self.get_table(o, community_suffix=community_suffix,
                           cached=cached)
            for o in oids
        ]
        if join == "left":
            lt = tables[1:]
            for k in sorted(tables[0]):
                yield tuple([k, tables[0][k]] + [t.get(k) for t in lt])
        elif join == "inner":
            keys = set(tables[0])
            for lt in tables[1:]:
                keys &= set(lt)
            for k in sorted(keys):
                yield tuple([k] + [t.get(k) for t in tables])
        elif join == "outer":
            keys = set(tables[0])
            for lt in tables[1:]:
                keys |= set(lt)
            for k in sorted(keys):
                yield tuple([k] + [t.get(k) for t in tables])
