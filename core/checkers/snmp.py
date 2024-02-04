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
from .base import Checker, CheckResult, Check
from ..script.scheme import Protocol, SNMPCredential, SNMPv3Credential
from noc.core.ioloop.snmp import snmp_get, SNMPError
from noc.core.ioloop.util import run_sync
from noc.core.snmp.version import SNMP_v1, SNMP_v2c
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.text import safe_shadow
from noc.core.comp import smart_text
from noc.core.mib import mib
from noc.config import config

CHECK_OIDS = [mib["SNMPv2-MIB::sysObjectID.0"]]


class SNMPProtocolChecker(Checker):
    """
    Check ManagedObject supported access protocols and credential
    """

    name = "snmp"
    CHECKS: List[str] = ["SNMPv1", "SNMPv2c", "SNMPv3"]
    PROTO_CHECK_MAP: Dict[str, Protocol] = {p.config.check: p for p in Protocol if p.config.check}
    SNMP_TIMEOUT_SEC = 3

    def iter_result(self, checks: List[Check]) -> Iterable[CheckResult]:
        """ """
        # Group by address
        processed = {}
        for c in checks:
            if c.name not in self.CHECKS:
                continue
            key = (c.address, c.port)
            if key not in processed:
                processed[key] = defaultdict(set)
            for cred in c.credentials:
                processed[key][cred].add(c)
        # Process checks
        for (address, port), cc in processed.items():
            for cred, checks in cc.items():
                for c in checks:
                    r = run_sync(partial(self.do_snmp_check, c, cred))
                    yield r

    async def do_snmp_check(
        self, check: Check, cred: Union[SNMPCredential, SNMPv3Credential]
    ) -> CheckResult:
        """

        :param check:
        :param cred:
        :return:
        """
        if self.pool and isinstance(cred, SNMPv3Credential):
            status, message = self.check_v3_oid_on_pool(
                check.address,
                check.port,
                cred.oids or CHECK_OIDS,
                cred.username,
                cred.snmp_auth_proto,
                cred.auth_key,
                cred.private_proto,
                cred.private_key,
                self.SNMP_TIMEOUT_SEC,
            )
        elif not self.pool and isinstance(cred, SNMPv3Credential):
            raise NotImplementedError("Direct SNMPv3 is not implemented yet")
        elif not self.pool and isinstance(cred, SNMPCredential):
            status, message = await self.check_v2_oid(
                check.address,
                check.port,
                cred.oids or CHECK_OIDS,
                cred.snmp_ro,
                SNMP_v2c if check.name == "SNMPv2c" else SNMP_v1,
                self.SNMP_TIMEOUT_SEC,
            )
        else:
            status, message = self.check_v2_oid_on_pool(
                check.address,
                check.port,
                cred.oids or CHECK_OIDS,
                cred.snmp_ro,
                SNMP_v2c if check.name == "SNMPv2c" else SNMP_v1,
                self.SNMP_TIMEOUT_SEC,
            )
        if not status and not message:
            message = "Nothing value in MIB View"
        # self.logger.info(
        #     "Guessed community: %s, version: %d",
        #     config.snmp_ro,
        #     config.protocol.config.snmp_version,
        # )
        return CheckResult(
            check=check.name,
            status=status,
            is_access=status,
            is_available=status or None,
            credentials=[cred] if status else [],
            error=message,
        )

    async def check_v2_oid(
        self,
        address,
        port,
        oids: List[str],
        community: str,
        version: int = SNMP_v2c,
        timeout: int = 3,
    ) -> Tuple[bool, str]:
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
            "Trying community '%s': %s, version: %s", safe_shadow(community), oids, version
        )
        self.logger.debug("Trying community '%s': %s, version: %s", community, oids, version)
        self.logger.debug("SNMP v2c GET %s %s", address, oids)
        message = ""
        try:
            result = await snmp_get(
                address=address,
                oids={o: o for o in oids},
                community=community,
                version=SNMP_v2c,
                tos=config.activator.tos,
                timeout=timeout,
            )
            self.logger.debug("SNMP GET %s %s returns %s", address, oids, result)
            result = smart_text(result, errors="replace") if result else result
        except SNMPError as e:
            result, message = False, repr(e)
            self.logger.debug("SNMP GET %s %s returns error %s", address, oids, e)
        except Exception as e:
            result, message = False, str(e)
            self.logger.debug("SNMP GET %s %s returns unknown error %s", address, oids, e)
        return bool(result), message

    def check_v2_oid_on_pool(
        self,
        address,
        port,
        oids: List[str],
        community: str,
        version: int = SNMP_v2c,
        timeout: int = 3,
    ) -> Tuple[bool, str]:
        """
        Perform SNMP GET. Param is OID or symbolic name, version is activator method
        todo mass check
        :param oids:
        :param community:
        :param version:
        :param timeout:
        :return:
        """
        oid = oids[0]
        self.logger.info(
            "Trying community '%s': %s, version: %s", safe_shadow(community), oid, version
        )
        self.logger.debug("Trying community '%s': %s, version: %s", community, oid, version)
        try:
            result, message = open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).__getattr__(version)(address, community, oid, timeout, True)
            if message.startswith("<"):
                message = message.strip("<>")
            self.logger.info("Result: %s (%s)", result, message)
            return result is not None, message or ""
        except RPCError as e:
            self.logger.info("RPC Error: %s", e)
            return False, str(e)

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
    ) -> Tuple[bool, str]:
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
            return result is not None, message or ""
        except RPCError as e:
            self.logger.info("RPC Error: %s", e)
            return False, str(e)
