# ----------------------------------------------------------------------
# SNMP methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from functools import partial
from typing import Optional, Dict, Callable, List, Union, Tuple, Any
import weakref

# Third-party modules
from gufo.snmp import SnmpSession, SnmpVersion, SnmpError as GSNMPError
from gufo.snmp.user import User, Aes128Key, DesKey, Md5Key, Sha1Key, KeyType


# NOC modules
from noc.core.snmp.error import SNMPError, BAD_VALUE, TIMED_OUT
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
from noc.core.mib import mib


GUFO_SNMP_VERSION_MAP = {
    SNMP_v1: SnmpVersion.v1,
    SNMP_v2c: SnmpVersion.v2c,
    SNMP_v3: SnmpVersion.v3,
}
BULK_MAX_REPETITIONS = 20

AUTH_PROTO_MAP = {
    "MD5": Md5Key,
    "SHA": Sha1Key,
}

PRIV_PROTO_MAP = {
    "DES": DesKey,
    "AES": Aes128Key,
}


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
        self.rate_limit = rate

    def _get_auth_key(self) -> Union[Md5Key, Sha1Key]:
        """
        Getting SNMPv3 Authenticate Key
        """
        if not self.script.credentials["snmp_auth_key"]:
            raise SNMPError("Unknown Authentication Key")
        passphrase = self.script.credentials["snmp_auth_key"].encode("utf-8")
        return AUTH_PROTO_MAP[self.script.credentials["snmp_auth_proto"]](
            passphrase, key_type=KeyType.Password
        )

    def _get_private_key(self) -> Union[DesKey, Aes128Key]:
        """
        Getting SNMPv3 Private Key
        """
        if not self.script.credentials["snmp_priv_key"]:
            raise SNMPError("Unknown Private Key")
        passphrase = self.script.credentials["snmp_priv_key"].encode("utf-8")
        return PRIV_PROTO_MAP[self.script.credentials["snmp_priv_proto"]](
            passphrase, key_type=KeyType.Password
        )

    def _get_engine_id(self) -> Optional[bytes]:
        """
        Get SNMPv3 EngineId from Capabilities 'SNMP | EngineID'
        bytes.fromhex(engine_id[2:])
        """
        engine_id = self.script.capabilities.get("SNMP | EngineID")
        if not engine_id:
            return None
        return bytes.fromhex(engine_id)

    def _get_snmp_credential(self, version):
        version = self._get_snmp_version(version)
        if version < 3 and "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        elif version < 3:
            return str(self.script.credentials["snmp_ro"])
        elif "snmp_username" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        elif "snmp_priv_proto" in self.script.credentials:
            return User(
                name=str(self.script.credentials["snmp_username"]),
                auth_key=self._get_auth_key(),
                priv_key=self._get_private_key(),
            )
        elif "snmp_auth_proto" in self.script.credentials:
            return User(
                name=str(self.script.credentials["snmp_username"]), auth_key=self._get_auth_key()
            )
        return User(name=str(self.script.credentials["snmp_username"]))

    async def get_session(self, version=None) -> "SnmpSession":
        if not self.socket:
            self.logger.debug("Create UDP Session")
            version = self._get_snmp_version(version)
            config = {
                "addr": self.script.credentials["address"],
                "limit_rps": self.rate_limit,
                "version": GUFO_SNMP_VERSION_MAP[version],
                "timeout": 10,
                "tos": self.script.tos,
            }
            cred = self._get_snmp_credential(version)
            if isinstance(cred, str):
                config["community"] = cred
            else:
                config["community"] = ""
                config["user"] = cred
                config["engine_id"] = self._get_engine_id()
            self.socket = SnmpSession(**config)
            try:
                await self.socket.refresh()
            except TimeoutError:
                raise self.SNMPError(code=TIMED_OUT)
        return self.socket

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
            # self.socket.close()
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
            elif "snmp_username" in self.script.credentials:
                self.snmp_version = SNMP_v3
            elif "snmp_ro" in self.script.credentials:
                self.snmp_version = SNMP_v2c
            else:
                raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        return self.snmp_version

    def _get_display_hints(self):
        if self.display_hints is None:
            self.display_hints = self.script.profile.get_snmp_display_hints(self.script)
        return self.display_hints

    def _get_snmp_credentials(self, version: Optional[int] = None) -> Tuple[str, int]:
        version = self._get_snmp_version(version)
        if self.script.is_beefed:
            return "public", SNMP_v2c
        elif version < SNMP_v3 and "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        elif version < SNMP_v3:
            return str(self.script.credentials["snmp_ro"]), version
        raise NotImplementedError("Native SNMP backend is not supported v3")

    def get(
        self,
        oids: Union[Dict[str, str], str],
        cached: bool = False,
        version: Optional[int] = None,
        timeout: int = 10,
        raw_varbinds=False,
        display_hints: Optional[Dict[str, Callable]] = None,
    ) -> Union[Any, Dict[str, Any]]:
        """
        Perform SNMP GET request by gufo_snmp library
        :param oids: dict with oids in form {name: oid, ...} or string contains oid
        :param cached: True if get results can be cached during session
        :param version: SNMP Version used, if None - SNMP Capabilities used
        :param timeout: Timeout for SNMP Response
        :param raw_varbinds: Return value in BER encoding
        :param display_hints: Dict of  oid -> render_function. See BaseProfile.snmp_display_hints for details
        :returns: eigther result scalar or dict of name -> value
        """

        async def run():
            address = self.script.credentials["address"]
            self.logger.debug("[%s] SNMP GET %s", address, oids)
            session = await self.get_session(version)
            try:
                data = await session.get_many(oids)
            except TimeoutError:
                if self.timeouts_limit:
                    self.timeouts -= 1
                    if not self.timeouts:
                        raise self.FatalTimeoutError()
                raise self.TimeOutError()
            except GSNMPError as e:
                self.logger.error("SNMP error code %s", e)
                raise self.SNMPError(code=e)
            # Render data if it has display hint
            for k in data:
                if isinstance(data[k], bytes):
                    data[k] = mib.render(k, data[k], display_hints)
            # Transform result to common format
            if oid_map:
                result = {}
                for k, v in data.items():
                    if k in oid_map:
                        result[oid_map[k]] = v
                    else:
                        self.logger.error("[%s] Invalid oid %s returned in reply", address, k)
            elif data:
                result = data[oids[0]]
            else:
                # Device return empty varbinds, perhaps need more info
                raise SNMPError(code=BAD_VALUE, oid=oids)
            self.logger.debug("[%s] GET result: %r", address, result)
            return result

        if raw_varbinds:
            raise NotImplementedError(
                "`raw_varbinds` parameter is not supported in gufo SNMP implementation."
            )

        oid_map = {}
        if isinstance(oids, str):
            oids = [oids]
        elif isinstance(oids, dict):
            oid_map = {oids[k]: k for k in oids}
            oids = list(oids.values())
        else:
            raise ValueError("oids must be either string or dict")
        if display_hints is None:
            display_hints = self._get_display_hints()
        return run_sync(run, close_all=False)

    def set(self, *args):
        """
        Perform SNMP GET request by gufo_snmp library
        :param args:
        :returns:
        """
        raise NotImplementedError(
            "Method `set` is not yet implemented in gufo SNMP implementation."
        )

    def count(self, oid, filter=None, version=None, timeout: int = 10) -> int:
        """
        Iterate MIB subtree and count matching instances by gufo_snmp library
        :param oid: OID
        :param filter: Callable accepting oid and value and returning boolean
        :param timeout: Timeout for SNMP Response
        """

        async def run(filter: Callable):
            address = self.script.credentials["address"]
            self.logger.debug("[%s] SNMP COUNT %s", address, oid)
            session = await self.get_session(version)
            result = 0
            oids_iter = session.getnext(oid)
            if self.script.has_snmp_bulk():
                oids_iter = session.getbulk(oid, max_repetitions=self.get_max_repetitions())
            try:
                async for oid_, v in oids_iter:
                    if filter(oid_, v):
                        result += 1
            except TimeoutError:
                raise self.TimeOutError()
            except GSNMPError as e:
                self.logger.error("SNMP error code %s", e.code)
                raise self.SNMPError(code=e.code)
            self.logger.debug("[%s] COUNT result: %s", address, result)
            return result

        return run_sync(partial(run, filter or (lambda x, y: True)), close_all=False)

    def get_max_repetitions(self, max_repetitions: Optional[int] = None) -> Optional[int]:
        """Return max_repetition on SNMP Bulk Request"""
        max_repetitions = max_repetitions or BULK_MAX_REPETITIONS
        caps_limit = self.script.get_snmp_bulk_repetition()
        if caps_limit:
            max_repetitions = min(max_repetitions, caps_limit)
        return max_repetitions

    def getnext(
        self,
        oid: str,
        community_suffix: Optional[str] = None,
        filter=None,
        cached: bool = False,
        only_first: bool = False,
        bulk: Optional[bool] = None,
        max_repetitions: Optional[int] = None,
        version: Optional[int] = None,
        max_retries: int = 0,
        timeout: int = 10,
        raw_varbinds: bool = False,
        display_hints: Optional[Dict[str, Callable]] = None,
        max_records: Optional[int] = None,
    ) -> List[Tuple[str, Any]]:
        """
        Perform SNMP GETNEXT request by gufo_snmp library
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
        :param max_records: Return only set record count
        :returns: result in list of tuples (name, value)
        """

        async def run(max_retries, filter):
            address = self.script.credentials["address"]
            self.logger.debug(
                "[%s] SNMP GETNEXT%s %s",
                address,
                "(With Bulk)" if bulk else "",
                oid,
            )
            session = await self.get_session(version)
            oids_iter = session.getnext(oid)
            if bulk:
                oids_iter = session.getbulk(
                    oid, max_repetitions=self.get_max_repetitions(max_repetitions)
                )
            result = []
            while True:
                try:
                    async for oid_, v in oids_iter:
                        if not filter(oid_, v):
                            continue
                        if isinstance(v, bytes):
                            v = mib.render(oid_, v, display_hints)
                        result += [(oid_, v)]
                        if only_first:
                            break
                        if max_records and len(result) >= max_records:
                            break
                    self.logger.debug("[%s] GETNEXT result: %s", address, result)
                    return result
                except TimeoutError:
                    if not max_retries:
                        raise self.TimeOutError()
                    max_retries -= 1
                except GSNMPError as e:
                    self.logger.error("SNMP error code %s", e.code)
                    raise self.SNMPError(code=e.code)

        if raw_varbinds:
            raise NotImplementedError(
                "`raw_varbinds` parameter is not supported in gufo SNMP implementation."
            )
        bulk = self.script.has_snmp_bulk() if bulk is None else bulk
        if display_hints is None:
            display_hints = self._get_display_hints()
        return run_sync(partial(run, max_retries, filter or (lambda x, y: True)), close_all=False)

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

    def get_engine_id(self, *args):
        """
        Getting SNMPv3 EngineId from address
        """

        async def run():
            address = self.script.credentials["address"]
            self.logger.debug("[%s] SNMP GET EngineID", address)
            session = await self.get_session(SNMP_v3)
            try:
                return session.get_engine_id()
            except self.TimeOutError:
                return None

        return run_sync(run, close_all=False)
