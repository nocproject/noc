# ----------------------------------------------------------------------
# SNMP checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from functools import partial
from typing import List, Iterable, Dict, Tuple, Union, Optional

# NOC modules
from .base import Checker, CheckResult, Check, CheckError, DataItem
from ..script.scheme import Protocol, SNMPCredential, SNMPv3Credential
from noc.core.ioloop.snmp import snmp_get, SNMPError
from noc.core.ioloop.util import run_sync
from noc.core.snmp.version import SNMP_v3
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.text import safe_shadow
from noc.core.mib import mib
from noc.config import config

CHECK_OIDS = [mib["SNMPv2-MIB::sysObjectID.0"]]
SUGGEST_CHECK = "SUGGEST_SNMP"


class SNMPProtocolChecker(Checker):
    """
    Check ManagedObject supported access protocols and credential
    """

    name = "snmp"
    CHECKS: List[str] = ["SNMPv1", "SNMPv2c", "SNMPv3", SUGGEST_CHECK]
    PROTO_CHECK_MAP: Dict[str, Protocol] = {p.config.check: p for p in Protocol if p.config.check}
    SNMP_TIMEOUT_SEC = 3
    PARAMS = ["rules"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rules: List[Union[SNMPCredential, SNMPv3Credential]] = self.load_suggests(
            kwargs.get("rules")
        )

    @staticmethod
    def load_suggests(credentials):
        if not credentials:
            return []
        return [x for x in credentials if isinstance(x, (SNMPCredential, SNMPv3Credential))]

    def iter_suggest_check(self, check: Check) -> Iterable[Check]:
        """
        Iter all proto if suggest mode set
        :param check:
        :return:
        """
        if check.name != SUGGEST_CHECK:
            yield check
            return
        for c in self.CHECKS:
            if c == SUGGEST_CHECK:
                continue
            yield Check(
                name=c,
                address=check.address or self.address,
                port=check.port,
                args=check.args,
                credential=check.credential,
            )

    def iter_result(self, checks: List[Check]) -> Iterable[CheckResult]:
        """ """
        # Group by address
        processed = {}
        for check in checks:
            for c in self.iter_suggest_check(check):
                if c.name not in self.CHECKS:
                    continue
                if not c.credential and not self.rules:
                    continue
                key = (c.address, c.port)
                if key not in processed:
                    processed[key] = defaultdict(set)
                if c.credential:
                    processed[key][c.credential].add(c)
                for proto, cred in self.rules:
                    processed[key][cred].add(c)
        self.logger.debug("Processed SNMP checks: %s", processed)
        # Process checks
        result = {}
        for cc in processed.values():
            for cred, ccs in cc.items():
                for c in ccs:
                    if c in result:
                        continue
                    try:
                        skipped, data, message = run_sync(partial(self.do_snmp_check, c, cred))
                    except NotImplementedError:
                        continue
                    if skipped:
                        continue
                    status, error = not bool(message) and bool(data), None
                    if not status:
                        error = CheckError(
                            code="",
                            is_access=bool(data),
                            is_available=not bool(message),
                            message=message,
                        )
                    result[c] = CheckResult(
                        check=c.name,
                        args=c.args,
                        status=status,
                        data=data,
                        credential=cred if data else None,
                        error=error,
                    )
        for check in checks:
            for c in self.iter_suggest_check(check):
                if c in result:
                    yield result[c]
                else:
                    yield CheckResult(
                        check=c.name,
                        status=True,
                        skipped=True,
                    )
        # if any(c.status for c in result.values()):
        #     yield CheckResult(
        #         check=SUGGEST_CHECK,
        #         status=True,
        #     )

    async def do_snmp_check(
        self, check: Check, cred: Union[SNMPCredential, SNMPv3Credential]
    ) -> Tuple[bool, Optional[List[DataItem]], str]:
        """

        :param check:
        :param cred:
        :return: available, getting data, error text
        """
        protocol = self.PROTO_CHECK_MAP[check.name]
        if (
            protocol.config.snmp_version == SNMP_v3
            and self.pool
            and isinstance(cred, SNMPv3Credential)
        ):
            r, message = self.check_v3_oid_on_pool(
                check.address or self.address,
                check.port,
                cred.oids or CHECK_OIDS,
                cred.username,
                cred.auth_proto,
                cred.auth_key,
                cred.private_proto,
                cred.private_key,
                self.SNMP_TIMEOUT_SEC,
            )
        elif (
            protocol.config.snmp_version == SNMP_v3
            and not self.pool
            and isinstance(cred, SNMPv3Credential)
        ):
            raise NotImplementedError("Direct SNMPv3 is not implemented yet")
        elif (
            protocol.config.snmp_version != SNMP_v3
            and not self.pool
            and isinstance(cred, SNMPCredential)
        ):
            r, message = await self.check_v2_oid(
                check.address or self.address,
                check.port,
                cred.oids or CHECK_OIDS,
                cred.snmp_ro,
                protocol,
                self.SNMP_TIMEOUT_SEC,
            )
        elif protocol.config.snmp_version != SNMP_v3 and isinstance(cred, SNMPCredential):
            r, message = self.check_v2_oid_on_pool(
                check.address or self.address,
                check.port,
                cred.oids or CHECK_OIDS,
                cred.snmp_ro,
                protocol,
                self.SNMP_TIMEOUT_SEC,
            )
        else:
            return True, None, ""
        if not r and not message:
            message = "Nothing value in MIB View"
        # self.logger.info(
        #     "Guessed community: %s, version: %d",
        #     config.snmp_ro,
        #     config.protocol.config.snmp_version,
        # )
        if r:
            r = [DataItem(name=k, value=v) for k, v in r.items()]
        return False, r, message
        # return CheckResult(
        #     check=check.name,
        #     status=status,
        #     is_access=status,
        #     is_available=status or None,
        #     credentials=[cred] if status else [],
        #     error=message,
        # )

    async def check_v2_oid(
        self,
        address,
        port,
        oids: List[str],
        community: str,
        protocol: Protocol = Protocol(7),
        timeout: int = 3,
    ) -> Tuple[Optional[Dict[str, str]], str]:
        """
        Perform SNMP GET. Param is OID or symbolic name, version is activator method
        :param address:
        :param port:
        :param oids:
        :param community:
        :param version:
        :param timeout:
        :return:
        """
        self.logger.info(
            "Trying community '%s': %s, version: %s",
            safe_shadow(community),
            oids,
            protocol.config.alias,
        )
        self.logger.debug(
            "Trying community '%s': %s, version: %s", community, oids, protocol.config.alias
        )
        self.logger.debug("SNMP v2c GET %s %s", address, oids)
        message = ""
        try:
            result = await snmp_get(
                address=address,
                oids={o: o for o in oids},
                community=community,
                version=protocol.config.snmp_version,
                tos=config.activator.tos,
                timeout=timeout,
            )
            self.logger.debug("SNMP GET %s %s returns %s", address, oids, result)
            # result = smart_text(result, errors="replace") if result else result
        except SNMPError as e:
            result, message = None, repr(e)
            self.logger.debug("SNMP GET %s %s returns error %s", address, oids, e)
        except Exception as e:
            result, message = None, str(e)
            self.logger.debug("SNMP GET %s %s returns unknown error %s", address, oids, e)
        return result, message

    def check_v2_oid_on_pool(
        self,
        address,
        port,
        oids: List[str],
        community: str,
        protocol: Protocol = Protocol(7),
        timeout: int = 3,
    ) -> Tuple[Optional[Dict[str, str]], str]:
        """
        Perform SNMP GET. Param is OID or symbolic name, version is activator method
        todo mass check
        :param oids:
        :param community:
        :param protocol:
        :param timeout:
        :return:
        """
        oid = oids[0]
        self.logger.info(
            "Trying community '%s': %s, version: %s",
            safe_shadow(community),
            oid,
            protocol.config.alias,
        )
        self.logger.debug(
            "Trying community '%s': %s, version: %s", community, oid, protocol.config.alias
        )
        try:
            result, message = open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).__getattr__(f"{protocol.config.alias}_get")(address, community, oid, timeout, True)
            if message.startswith("<"):
                message = message.strip("<>")
            self.logger.info("Result: %s (%s)", result, message)
            return {oid: result} if result else None, message or ""
        except RPCError as e:
            self.logger.info("RPC Error: %s", e)
            return None, str(e)

    def check_v3_oid_on_pool(
        self,
        address,
        port,
        oids: List[str],
        username: str,
        auth_proto: Optional[str] = None,
        auth_key: Optional[str] = None,
        priv_proto: Optional[str] = None,
        priv_key: Optional[str] = None,
        timeout: int = 3,
    ) -> Tuple[Optional[Dict[str, str]], str]:
        """
        Perform SNMP GET. Param is OID or symbolic name, version is activator method
        todo mass check
        :param address:
        :param port:
        :param oids:
        :param username:
        :param auth_proto
        :param auth_key:
        :param priv_proto:
        :param priv_key:
        :param timeout:
        :return:
        """
        oid = oids[0]
        self.logger.info(
            "Trying community '%s': %s, version: %s", safe_shadow(username), oid, "SNMPv3"
        )
        self.logger.debug("Trying community '%s': %s, version: %s", username, oid, "SNMPv3")
        try:
            result, message = open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).snmp_v3_get(
                address, username, oid, auth_proto, auth_key, priv_proto, priv_key, timeout, True
            )
            if message.startswith("<"):
                message = message.strip("<>")
            self.logger.info("Result: %s (%s)", result, message)
            return {oid: result} if result else None, message or ""
        except RPCError as e:
            self.logger.info("RPC Error: %s", e)
            return None, str(e)
