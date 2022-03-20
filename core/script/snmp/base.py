# ----------------------------------------------------------------------
# SNMP methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Callable, List
import weakref

# NOC modules
from noc.core.ioloop.snmp import snmp_get, snmp_count, snmp_getnext, snmp_set
from noc.core.snmp.error import SNMPError, TIMED_OUT
from noc.core.snmp.version import SNMP_v1, SNMP_v2c, SNMP_v3
from noc.core.log import PrefixLoggerAdapter
from noc.core.ioloop.udp import UDPSocket
from noc.core.error import (
    NOCError,
    ERR_SNMP_TIMEOUT,
    ERR_SNMP_FATAL_TIMEOUT,
    ERR_SNMP_BAD_COMMUNITY,
)
from noc.core.ioloop.util import run_sync
from noc.core.ratelimit.asyncio import AsyncRateLimit


class SNMP(object):
    name = "snmp"

    class TimeOutError(NOCError):
        default_code = ERR_SNMP_TIMEOUT
        default_msg = "SNMP Timeout"

    class FatalTimeoutError(NOCError):
        default_code = ERR_SNMP_FATAL_TIMEOUT
        default_msg = "Fatal SNMP Timeout"

    SNMPError = SNMPError

    def __init__(self, script, rate: Optional[float] = None):
        self._script = weakref.ref(script)
        self.logger = PrefixLoggerAdapter(script.logger, self.name)
        self.timeouts_limit = 0
        self.timeouts = 0
        self.socket = None
        self.display_hints = None
        self.snmp_version = None
        self.rate_limit: Optional[AsyncRateLimit] = AsyncRateLimit(rate) if rate else None

    @property
    def script(self):
        return self._script()

    def set_timeout_limits(self, n):
        """
        Set sequental timeouts l
        :param n:
        :return:
        """
        self.timeouts_limit = n
        self.timeouts = n

    def close(self):
        if self.socket:
            self.logger.debug("Closing UDP socket")
            self.socket.close()
            self.socket = None

    def get_socket(self):
        if not self.socket:
            self.logger.debug("Create UDP socket")
            self.socket = UDPSocket(tos=self.script.tos)
        return self.socket

    def _get_snmp_version(self, version=None):
        if version is not None:
            return version
        if self.snmp_version is None:
            if self.script.has_snmp_v2c():
                self.snmp_version = SNMP_v2c
            elif self.script.has_snmp_v3():
                self.snmp_version = SNMP_v3
            elif self.script.has_snmp_v1():
                self.snmp_version = SNMP_v1
            else:
                self.snmp_version = SNMP_v2c
        return self.snmp_version

    def _get_display_hints(self):
        if self.display_hints is None:
            self.display_hints = self.script.profile.get_snmp_display_hints(self.script)
        return self.display_hints

    def get(
        self,
        oids: List[str],
        cached: bool = False,
        version: Optional[str] = None,
        raw_varbinds=False,
        display_hints: Optional[Dict[str, Callable]] = None,
    ):
        """
        Perform SNMP GET request
        :param List[str] oids: string or list of oids
        :param cached: True if get results can be cached during session
        :param version: SNMP Version used, if None - SNMP Capabilities used
        :param raw_varbinds: Return value in BER encoding
        :param display_hints: Dict of  oid -> render_function. See BaseProfile.snmp_display_hints for details
        :returns: eigther result scalar or dict of name -> value
        """

        async def run():
            try:
                r = await snmp_get(
                    address=self.script.credentials["address"],
                    oids=oids,
                    community=str(self.script.credentials["snmp_ro"]),
                    tos=self.script.tos,
                    udp_socket=self.get_socket(),
                    version=version,
                    raw_varbinds=raw_varbinds,
                    display_hints=display_hints,
                    response_parser=self.script.profile.get_snmp_response_parser(self.script),
                    rate_limit=self.rate_limit,
                )
                self.timeouts = self.timeouts_limit
                return r
            except SNMPError as e:
                if e.code == TIMED_OUT:
                    if self.timeouts_limit:
                        self.timeouts -= 1
                        if not self.timeouts:
                            raise self.FatalTimeoutError()
                    raise self.TimeOutError()
                else:
                    raise

        if "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        if display_hints is None:
            display_hints = self._get_display_hints()
        version = self._get_snmp_version(version)
        return run_sync(run, close_all=False)

    def set(self, *args):
        """
        Perform SNMP GET request
        :param oid: string or list of oids
        :returns: eigther result scalar or dict of name -> value
        """

        async def run():
            try:
                r = await snmp_set(
                    address=self.script.credentials["address"],
                    varbinds=varbinds,
                    community=str(self.script.credentials["snmp_rw"]),
                    tos=self.script.tos,
                    udp_socket=self.get_socket(),
                    rate_limit=self.rate_limit,
                )
                return r
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
        if "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        return run_sync(run, close_all=False)

    def count(self, oid, filter=None, version=None):
        """
        Iterate MIB subtree and count matching instances
        :param oid: OID
        :param filter: Callable accepting oid and value and returning boolean
        """

        async def run():
            try:
                r = await snmp_count(
                    address=self.script.credentials["address"],
                    oid=oid,
                    community=str(self.script.credentials["snmp_ro"]),
                    bulk=self.script.has_snmp_bulk(),
                    filter=filter,
                    tos=self.script.tos,
                    udp_socket=self.get_socket(),
                    version=version,
                    rate_limit=self.rate_limit,
                )
                return r
            except SNMPError as e:
                if e.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        if "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        version = self._get_snmp_version(version)
        return run_sync(run, close_all=False)

    def getnext(
        self,
        oid: str,
        community_suffix: Optional[str] = None,
        filter=None,
        cached: bool = False,
        only_first: bool = False,
        bulk: Optional[bool] = None,
        max_repetitions: Optional[int] = None,
        version: Optional[str] = None,
        max_retries: int = 0,
        timeout: int = 10,
        raw_varbinds: bool = False,
        display_hints: Optional[Dict[str, Callable]] = None,
    ):
        """
        Perform SNMP GETNEXT request
        :param oid: string
        :param community_suffix:
        :param filter:
        :param cached: True if get results can be cached during session
        :param only_first: Return first result
        :param bulk: False - disable GetBulk, None - Enable by 'SNMP | Bulk' capabilities
        :param max_repetitions: Max OID in Bulk result
        :param version: SNMP Version: 0 - v1, 1 - v2c
        :param max_retries: Mac count trying when no response
        :param timeout: Timeout for SNMP Response
        :param raw_varbinds: Return value in BER encoding
        :param display_hints: Dict of  oid -> render_function. See BaseProfile.snmp_display_hints for details
        :returns: eigther result scalar or dict of name -> value
        """

        async def run():
            try:
                r = await snmp_getnext(
                    address=self.script.credentials["address"],
                    oid=oid,
                    community=str(self.script.credentials["snmp_ro"]),
                    bulk=self.script.has_snmp_bulk() if bulk is None else bulk,
                    max_repetitions=max_repetitions,
                    filter=filter,
                    only_first=only_first,
                    tos=self.script.tos,
                    udp_socket=self.get_socket(),
                    version=version,
                    max_retries=max_retries,
                    timeout=timeout,
                    raw_varbinds=raw_varbinds,
                    display_hints=display_hints,
                    response_parser=self.script.profile.get_snmp_response_parser(self.script),
                    rate_limit=self.rate_limit,
                )
                return r
            except SNMPError as e:
                if e.code == TIMED_OUT:
                    raise self.TimeOutError()
                else:
                    raise

        if "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        if display_hints is None:
            display_hints = self._get_display_hints()
        version = self._get_snmp_version(version)
        return run_sync(run, close_all=False)

    def get_table(self, oid, community_suffix=None, cached=False, display_hints=None):
        """
        GETNEXT wrapper. Returns a hash of <index> -> <value>
        """
        r = {}
        for o, v in self.getnext(
            oid, community_suffix=community_suffix, cached=cached, display_hints=display_hints
        ):
            r[int(o.split(".")[-1])] = v
        return r

    def join_tables(self, oid1, oid2, community_suffix=None, cached=False, display_hints=None):
        """
        Generator returning a rows of two snmp tables joined by index
        """
        t1 = self.get_table(
            oid1, community_suffix=community_suffix, cached=cached, display_hints=display_hints
        )
        t2 = self.get_table(
            oid2, community_suffix=community_suffix, cached=cached, display_hints=display_hints
        )
        for k1, v1 in t1.items():
            try:
                yield v1, t2[k1]
            except KeyError:
                pass

    def get_tables(
        self,
        oids: List[str],
        community_suffix: str = None,
        bulk: Optional[bool] = None,
        min_index: Optional[int] = None,
        max_index: Optional[int] = None,
        cached: Optional[bool] = False,
        max_repetitions: Optional[int] = None,
        timeout: int = 15,
        max_retries: int = 0,
        display_hints: Optional[Dict[str, Callable]] = None,
    ):
        """
        Query list of SNMP tables referenced by oids and yields
        tuples of (key, value1, ..., valueN)

        :param oids: List of OIDs
        :param community_suffix: Optional suffix to be added to community
        :param bulk: Use BULKGETNEXT if true
        :param min_index:
        :param max_index:
        :param cached:
        :param max_repetitions: Max OID in Bulk result
        :param max_retries: Mac count trying when no response
        :param timeout: Timeout for SNMP Response
        :param display_hints: Dict of  oid -> render_function. See BaseProfile.snmp_display_hints for details
        :return:
        """

        def gen_table(oid):
            line = len(oid) + 1
            for o, v in self.getnext(
                oid,
                community_suffix=community_suffix,
                cached=cached,
                bulk=bulk,
                max_repetitions=max_repetitions,
                max_retries=max_retries,
                display_hints=display_hints,
                timeout=timeout,
            ):
                yield tuple([int(x) for x in o[line:].split(".")]), v

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
        tables = [self.get_table(o, community_suffix=community_suffix, cached=cached) for o in oids]
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

    def get_chunked(self, oids, chunk_size=20, timeout_limits=3):
        """
        Fetch list of oids splitting to several operations when necessary

        :param oids: List of oids
        :param chunk_size: Maximal GET chunk size
        :param timeout_limits: SNMP timeout limits
        :return: dict of oid -> value for all retrieved values
        """
        results = {}
        self.set_timeout_limits(timeout_limits)
        while oids:
            chunk, oids = oids[:chunk_size], oids[chunk_size:]
            chunk = {x: x for x in chunk}
            try:
                results.update(self.get(chunk))
            except self.TimeOutError as e:
                self.logger.error("Failed to get SNMP OIDs %s: %s", oids, e)
            except self.FatalTimeoutError:
                self.logger.error("Fatal timeout error on: %s", oids)
                break
            except self.SNMPError as e:
                self.logger.error("SNMP error code %s", e.code)
        return results
