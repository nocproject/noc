# ----------------------------------------------------------------------
# SNMP checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import List, Iterable, Dict, Tuple, Union, Optional, Any

# Third-party modules
from gufo.snmp.sync_client import SnmpSession as SyncSnmpSession
from gufo.snmp.async_client import SnmpSession as AsyncSnmpSession
from gufo.snmp import SnmpVersion, SnmpError as GSNMPError
from gufo.snmp._fast import SnmpAuthError
from gufo.snmp.user import User, Aes128Key, DesKey, Md5Key, Sha1Key, KeyType

# NOC modules
from noc.core.checkers.base import Checker, CheckResult, Check, CheckError, DataItem
from noc.core.script.scheme import Protocol, SNMPCredential, SNMPv3Credential
from noc.core.snmp.error import SNMPErrorCode
from noc.core.mib import mib

CHECK_OIDS = [mib["SNMPv2-MIB::sysObjectID.0"]]
SUGGEST_CHECK = "SUGGEST_SNMP"
AUTH_PROTO_MAP = {
    "MD5": Md5Key,
    "SHA": Sha1Key,
}

PRIV_PROTO_MAP = {
    "DES": DesKey,
    "AES": Aes128Key,
}


class SNMPProtocolChecker(Checker):
    """
    Check ManagedObject supported access protocols and credential
    """

    name = "snmp"
    CHECKS: List[str] = [
        Protocol.SNMPv1.config.check,
        Protocol.SNMPv2c.config.check,
        Protocol.SNMPv3.config.check,
    ]
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
        return [x for _, x in credentials if isinstance(x, (SNMPCredential, SNMPv3Credential))]

    @staticmethod
    def get_oids(check: Check, cred=None) -> List[str]:
        if check.args and "oids" in check.args:
            return check.args["oids"].split(",")
        elif check.credential and check.credential.oids:
            return check.credential.oids
        elif cred and cred.oids:
            return cred.oids
        return CHECK_OIDS

    def iter_suggest_check(self, check: Check) -> Iterable[Check]:
        """
        Iter all proto if suggest mode set
        Args:
            check: List processed checks
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

    def get_checks_by_address(
        self, checks: List[Check]
    ) -> Dict[
        Tuple[str, Optional[int]], Dict[Union[SNMPCredential, SNMPv3Credential], List[Check]]
    ]:
        """Group checks by address"""
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
                for cred in self.rules:
                    if isinstance(cred, SNMPCredential) and c.name == "SNMPv3":
                        continue
                    if isinstance(cred, SNMPv3Credential) and c.name != "SNMPv3":
                        continue
                    processed[key][cred].add(c)
        return processed

    async def iter_result_async(self, checks: List[Check]) -> Iterable[CheckResult]:
        """ """
        processed = self.get_checks_by_address(checks)
        # Process checks
        result = {}
        for cc in processed.values():
            for cred, ccs in cc.items():
                for c in ccs:
                    if c in result and result[c].status:
                        continue
                    if not c.address:
                        continue
                    data, error = await self.check_oids_async(
                        c.address, self.get_oids(c, cred), cred
                    )
                    result[c] = CheckResult(
                        check=c.name,
                        address=c.address,
                        port=c.port,
                        args=c.args,
                        status=not error,
                        data=[DataItem(name=k, value=v) for k, v in data.items()] if data else None,
                        credential=cred if data else None,
                        error=error,
                    )
        # Process checks
        for check in checks:
            for c in self.iter_suggest_check(check):
                if c in result:
                    yield result[c]
                else:
                    yield CheckResult(
                        check=c.name,
                        address=c.address,
                        port=c.port,
                        args=c.args,
                        status=True,
                        skipped=True,
                    )

    def iter_result(self, checks: List[Check]) -> Iterable[CheckResult]:
        """ """
        processed = self.get_checks_by_address(checks)
        self.logger.info("Processed SNMP checks: %s", processed)
        # Process checks
        result = {}
        for cc in processed.values():
            for cred, ccs in cc.items():
                for c in ccs:
                    if c in result and result[c].status:
                        continue
                    if not c.address:
                        continue
                    # skipped, data, message = run_sync(partial(self.do_snmp_check, c, cred))
                    data, error = self.check_oids_sync(c.address, self.get_oids(c), cred)
                    result[c] = CheckResult(
                        check=c.name,
                        address=c.address,
                        port=c.port,
                        args=c.args,
                        status=not error,
                        data=[DataItem(name=k, value=v) for k, v in data.items()] if data else None,
                        credential=cred,
                        error=error,
                    )
        self.logger.info("[XXXX] Processed checks result: %s", result)
        for check in checks:
            for c in self.iter_suggest_check(check):
                if c in result:
                    yield result[c]
                else:
                    yield CheckResult(
                        check=c.name,
                        address=c.address,
                        port=c.port,
                        args=c.args,
                        status=True,
                        skipped=True,
                    )
        # if any(c.status for c in result.values()):
        #     yield CheckResult(
        #         check=SUGGEST_CHECK,
        #         status=True,
        #     )

    @staticmethod
    def get_snmpv3_user(cred: SNMPv3Credential) -> User:
        """Build SNMPv3 user credential"""
        if cred.private_proto and cred.private_key:
            return User(
                name=cred.username,
                auth_key=AUTH_PROTO_MAP[cred.auth_proto](
                    cred.auth_key.encode(), key_type=KeyType.Password
                ),
                priv_key=PRIV_PROTO_MAP[cred.private_proto](
                    cred.private_key.encode(), key_type=KeyType.Password
                ),
            )
        elif cred.auth_proto and cred.auth_key:
            return User(
                name=cred.username,
                auth_key=AUTH_PROTO_MAP[cred.auth_proto](
                    cred.auth_key.encode(), key_type=KeyType.Password
                ),
            )
        return User(name=cred.username)

    @classmethod
    def get_session_config(
        cls,
        address,
        cred: Union[SNMPCredential, SNMPv3Credential],
        timeout: int = 1,
    ) -> Dict[str, Any]:
        """Build GufoSNMP Session config"""
        config = {
            "addr": address,
            # "limit_rps": self.rate_limit,
            # "version": GUFO_SNMP_VERSION_MAP[version],
            "timeout": timeout or cls.SNMP_TIMEOUT_SEC,
            # "tos": self.script.tos,
        }
        if isinstance(cred, SNMPCredential):
            config["community"] = cred.snmp_ro
            config["version"] = SnmpVersion.v2c
        elif isinstance(cred, SNMPv3Credential):
            config["user"] = cls.get_snmpv3_user(cred)
            config["version"] = SnmpVersion.v3
            # config["engine_id"] = self._get_engine_id()
        return config

    def check_oids_sync(
        self,
        address,
        oids: List[str],
        cred: Union[SNMPCredential, SNMPv3Credential],
        port: Optional[int] = None,
        protocol: Optional[Protocol] = None,
        timeout: int = 3,
    ) -> Tuple[Optional[Dict[str, str]], Optional[CheckError]]:
        cfg = self.get_session_config(address, cred, timeout=timeout)
        self.logger.debug(
            "Trying community '%s': %s, version: %s",
            cred,
            ";".join(oids),
            cfg,  # protocol.config.alias,
        )
        try:
            with SyncSnmpSession(**cfg) as session:
                data = session.get_many(oids)
        except TimeoutError:
            self.logger.debug("SNMP Timeout")
            return None, CheckError(
                code=str(SNMPErrorCode.TIMED_OUT), message="Timeout", is_available=False
            )
        except OSError as e:
            # Destination unreachable
            self.logger.debug("Destination unreachable")
            return None, CheckError(
                code=str(SNMPErrorCode.UNREACHABLE), message=e.args[0], is_available=False
            )
        except SnmpAuthError:
            self.logger.debug("SNMPv3 Authentication error")
            return None, CheckError(
                code=str(SNMPErrorCode.AUTHORIZATION_ERROR),
                message="Authentication Error",
                is_available=True,
                is_access=False,
            )
        except GSNMPError as e:
            self.logger.debug("SNMP error code %s", e)
            return None, CheckError(code=e.cide, message=str(e), is_available=False)
        # Render data if it has display hint
        for k in data:
            if isinstance(data[k], bytes):
                data[k] = mib.render(k, data[k])
        #  "Nothing value in MIB View"
        return data, None

    async def check_oids_async(
        self,
        address,
        oids: List[str],
        cred: Union[SNMPCredential, SNMPv3Credential],
        port: Optional[int] = None,
        protocol: Optional[Protocol] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, str]], Optional[CheckError]]:
        cfg = self.get_session_config(address, cred, timeout=timeout)
        self.logger.debug(
            "Trying community '%s': %s, version: %s",
            cred,
            ";".join(oids),
            cfg,  # protocol.config.alias,
        )
        try:
            async with AsyncSnmpSession(**cfg) as session:
                data = await session.get_many(oids)
        except TimeoutError:
            self.logger.debug("SNMP Timeout")
            return None, CheckError(
                code=str(SNMPErrorCode.TIMED_OUT), message="Timeout", is_available=False
            )
        except OSError as e:
            # Destination unreachable
            self.logger.debug("Destination unreachable")
            return None, CheckError(
                code=str(SNMPErrorCode.UNREACHABLE), message=e.args[0], is_available=False
            )
        except SnmpAuthError:
            self.logger.debug("SNMPv3 Authentication error")
            return None, CheckError(
                code=str(SNMPErrorCode.AUTHORIZATION_ERROR),
                message="Authentication Error",
                is_available=True,
                is_access=False,
            )
        except GSNMPError as e:
            self.logger.debug("SNMP error code %s", e)
            return None, CheckError(code="1", message=str(e), is_available=False)
        # Render data if it has display hint
        for k in data:
            if isinstance(data[k], bytes):
                data[k] = mib.render(k, data[k])
        # "Nothing value in MIB View"
        return data, None
