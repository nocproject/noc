# ----------------------------------------------------------------------
# SNMP based on gufo_snmp library
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Third-party modules
from gufo.snmp import SnmpSession, SnmpVersion, SnmpError as GSNMPError


# NOC modules
from noc.core.snmp.error import SNMPError, BAD_VALUE
from noc.core.error import ERR_SNMP_BAD_COMMUNITY
from noc.core.ioloop.util import run_sync
from noc.core.mib import mib
from .base import SNMP

GUFO_SNMP_VERSION_MAP = {
    0: SnmpVersion.v1,
    1: SnmpVersion.v2c,
}
BULK_MAX_REPETITIONS = 20


class GufoSNMP(SNMP):
    name = "gufo_snmp"

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
            self.logger.debug("[%s] SNMP GET %s", address, oids)
            async with SnmpSession(
                addr=address,
                community=str(self.script.credentials["snmp_ro"]),
                version=GUFO_SNMP_VERSION_MAP[version],
                timeout=timeout,
                tos=self.script.tos,
                limit_rps=self.rate_limit,
            ) as session:
                try:
                    data = await session.get_many(oids)
                except TimeoutError:
                    if self.timeouts_limit:
                        self.timeouts -= 1
                        if not self.timeouts:
                            raise self.FatalTimeoutError()
                    raise self.TimeOutError()
                except GSNMPError as e:
                    self.logger.error("SNMP error code %s", e.code)
                    raise self.SNMPError(code=e.code)
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
                "Use native SNMP implementation. Set config.activator.snmp_backend to 'native'"
            )
        address = self.script.credentials["address"]
        oid_map = {}
        if isinstance(oids, str):
            oids = [oids]
        elif isinstance(oids, dict):
            oid_map = {oids[k]: k for k in oids}
            oids = list(oids.values())
        else:
            raise ValueError("oids must be either string or dict")
        if "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        if display_hints is None:
            display_hints = self._get_display_hints()
        version = self._get_snmp_version(version)
        if version not in GUFO_SNMP_VERSION_MAP:
            raise ValueError(f"SNMP-version ({version}) is not supported by GufoSNMP library")
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
        version: Optional[int] = None,
        max_retries: int = 0,
        timeout: int = 10,
        raw_varbinds: bool = False,
        display_hints: Optional[Dict[str, Callable]] = None,
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
        :returns: result in list of tuples (name, value)
        """

        async def run(max_retries, filter):
            def true(x, y):
                return True

            self.logger.debug("[%s] SNMP GETNEXT %s", address, oid)
            if not filter:
                filter = true
            async with SnmpSession(
                addr=address,
                community=str(self.script.credentials["snmp_ro"]),
                version=GUFO_SNMP_VERSION_MAP[version],
                timeout=timeout,
                tos=self.script.tos,
                limit_rps=self.rate_limit,
            ) as session:
                oids_iter = session.getnext(oid)
                if bulk:
                    oids_iter = session.getbulk(
                        oid, max_repetitions=max_repetitions or BULK_MAX_REPETITIONS
                    )
                result = []
                while True:
                    try:
                        async for oid_, v in oids_iter:
                            if filter(oid_, v):
                                v = (
                                    mib.render(oid_, v, display_hints)
                                    if isinstance(v, bytes)
                                    else v
                                )
                                result += [(oid_, v)]
                        if only_first and result:
                            result = result[0:1]
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
                "Use native SNMP implementation. Set config.activator.snmp_backend to 'native'"
            )
        address = self.script.credentials["address"]
        bulk = self.script.has_snmp_bulk() if bulk is None else bulk
        if "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        if display_hints is None:
            display_hints = self._get_display_hints()
        version = self._get_snmp_version(version)
        if version not in GUFO_SNMP_VERSION_MAP:
            raise ValueError(f"SNMP-version ({version}) is not supported by GufoSNMP library")
        return run_sync(partial(run, max_retries, filter), close_all=False)

    def count(self, oid, filter=None, version=None, timeout: int = 10) -> int:
        """
        Iterate MIB subtree and count matching instances by gufo_snmp library
        :param oid: OID
        :param filter: Callable accepting oid and value and returning boolean
        :param timeout: Timeout for SNMP Response
        """

        async def run(filter):
            def true(x, y):
                return True

            self.logger.debug("[%s] SNMP COUNT %s", address, oid)
            if not filter:
                filter = true
            result = 0
            async with SnmpSession(
                addr=address,
                community=str(self.script.credentials["snmp_ro"]),
                version=GUFO_SNMP_VERSION_MAP[version],
                timeout=timeout,
                tos=self.script.tos,
                limit_rps=self.rate_limit,
            ) as session:
                oids_iter = session.getnext(oid)
                if self.script.has_snmp_bulk():
                    oids_iter = session.getbulk(oid, max_repetitions=BULK_MAX_REPETITIONS)
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

        address = self.script.credentials["address"]
        if "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        version = self._get_snmp_version(version)
        if version not in GUFO_SNMP_VERSION_MAP:
            raise ValueError(f"SNMP-version ({version}) is not supported by GufoSNMP library")
        return run_sync(partial(run, filter), close_all=False)

    def set(self, *args):
        """
        Perform SNMP GET request by gufo_snmp library
        :param args:
        :returns:
        """
        raise NotImplementedError(
            "Method `set` is not yet implemented in gufo SNMP implementation."
            "Use native SNMP implementation. Set config.activator.snmp_backend to 'native'"
        )

    def get_chunked(self, oids, chunk_size=20, timeout_limits=3):
        """
        Fetch list of oids splitting to several operations when necessary

        :param oids: List of oid
        :param chunk_size: Maximal GET chunk size
        :param timeout_limits: SNMP timeout limits
        :return: dict of oid -> value for all retrieved values
        """

        async def run():
            results = {}
            oo = oids[:]
            async with SnmpSession(
                addr=self.script.credentials["address"],
                community=str(self.script.credentials["snmp_ro"]),
                version=SnmpVersion.v2c if version == 1 else SnmpVersion.v1,
                tos=self.script.tos,
            ) as session:
                while oo:
                    chunk, oo = oo[:chunk_size], oo[chunk_size:]
                    try:
                        results.update(await session.get_many(chunk))
                    except TimeoutError:
                        if self.timeouts_limit:
                            self.timeouts -= 1
                            if not self.timeouts:
                                # Fatal SNMP Timeout
                                self.logger.error("Fatal timeout error on: %s", oids)
                                break
                        self.logger.error("Failed to get SNMP OIDs %s", chunk)
                        # raise self.TimeOutError()
                    except GSNMPError as e:
                        self.logger.error("SNMP error code %s", e.code)
                        raise self.SNMPError(code=e.code)
            return results

        self.set_timeout_limits(timeout_limits)
        if "snmp_ro" not in self.script.credentials:
            raise SNMPError(code=ERR_SNMP_BAD_COMMUNITY)
        # if display_hints is None:
        #     display_hints = self._get_display_hints()
        version = self._get_snmp_version()
        return run_sync(run, close_all=False)
