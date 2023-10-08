# ----------------------------------------------------------------------
# Credential checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple, Union, Iterator, Iterable

# Third-party modules
from pymongo import ReadPreference
from mongoengine.queryset.visitor import Q as m_q

# NOC modules
from .scheme import Protocol
from noc.core.log import PrefixLoggerAdapter
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.text import safe_shadow
from noc.sa.models.profile import Profile
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.core.mib import mib

CHECK_OIDS = [mib["SNMPv2-MIB::sysObjectID.0"]]
# mib["SNMPv2-MIB::sysUpTime.0"]
# mib["SNMPv2-MIB::sysDescr.0"]


@dataclass(frozen=True)
class SNMPCredential(object):
    snmp_ro: str = None
    snmp_rw: Optional[str] = None
    oids: Optional[List[str]] = None


@dataclass(frozen=True)
class CLICredential(object):
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None
    raise_privilege: bool = True


@dataclass(frozen=True)
class SuggestSNMPConfig(object):
    protocols: Tuple[Protocol, ...]
    check_method: str = "snmp_check"
    snmp_ro: Optional[str] = None
    snmp_rw: Optional[str] = None
    check_oids: Optional[Tuple[str, ...]] = None

    def get_credential(self) -> SNMPCredential:
        return SNMPCredential(self.snmp_ro, self.snmp_rw, oids=self.check_oids)


@dataclass(frozen=True)
class SuggestCLIConfig(object):
    protocols: Tuple[Protocol, ...]
    check_method: str = "cli_check"
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None
    raise_privileges: bool = True
    access_preference: Optional[str] = "C"

    def get_credential(self) -> CLICredential:
        return CLICredential(
            user=self.user,
            password=self.password,
            super_password=self.super_password,
            raise_privilege=self.raise_privileges,
        )


@dataclass(frozen=True)
class ProtocolResult(object):
    protocol: Protocol
    status: bool
    skipped: bool = False
    error: Optional[str] = None
    credential: Optional[Union[CLICredential, SNMPCredential]] = None


SUGGEST_SNMP: Tuple[Protocol, ...] = (Protocol(7), Protocol(6))
SUGGEST_CLI: Tuple[Protocol, ...] = (Protocol(1), Protocol(2))
SUGGEST_PROTOCOLS: Tuple[Protocol, ...] = SUGGEST_SNMP + SUGGEST_CLI


class CredentialChecker(object):
    """
    Credential checker for CLI/SNMP credential. Allow suggests credential
    """

    base_logger = logging.getLogger("credentialchecker")

    def __init__(
        self,
        address,
        pool,
        labels: List[str] = None,
        port: Optional[str] = None,
        logger=None,
        profile: Optional[str] = None,
        raise_privilege: bool = True,
        calling_service: str = "credentialchecker",
        credentials: Optional[List[Union[SuggestCLIConfig, SuggestSNMPConfig]]] = None,
        ignoring_rule: bool = False,
    ):
        """

        :param address: Device IP address
        :param pool: Activator pool for request
        :param labels: List labels for filter CredentialCheck Rules
        :param logger: logging instance
        :param profile: SA Profile
        :param raise_privilege: Try raise privilege for check
        :param calling_service: Service name
        :param credentials: Custom credential for check
        :param ignoring_rule: Do not use rule for suggest credential
        """
        self.address = address
        self.pool = pool
        self.port = port
        self.labels = labels
        self.logger = PrefixLoggerAdapter(
            logger or self.base_logger, "%s][%s" % (self.pool or "", self.address or "")
        )
        self.calling_service = calling_service
        self.profile: Optional["Profile"] = profile
        if isinstance(self.profile, str):
            self.profile = Profile.get_by_name(profile) if profile else None
        self.credentials: List[Union[CLICredential, SNMPCredential]] = credentials or []
        self.ignoring_rule = ignoring_rule
        self.ignoring_cli = False
        self.raise_privilege = raise_privilege
        if self.profile is None or self.profile.is_generic:
            self.logger.info("CLI Access for Generic profile is not supported. Ignoring")
            self.ignoring_cli = True

    @staticmethod
    def iter_protocols(*args, order: Tuple[Protocol, ...] = None) -> Iterable[Protocol]:
        """

        :param args:
        :param order:
        :return:
        """
        for p in sorted(
            set(args[0]).intersection(*[set(s) for s in args[1:] if s]),
            key=lambda x: order.index(x),
        ):
            yield p

    @staticmethod
    def is_unsupported_error(message) -> bool:
        """
        Todo replace to error_code
        :param message:
        :return:
        """
        if "Exception: TimeoutError()" in message:
            return True
        if "Error: Connection refused" in message:
            return True
        if "Error: Connection reset" in message:
            return True
        if "No supported authentication methods" in message:
            return True
        # if "SNMP Timeout" in message:
        #     return True
        return False

    def iter_suggests(
        self, protocols: Tuple[Protocol, ...] = None
    ) -> Iterator[Union[SuggestCLIConfig, SuggestSNMPConfig]]:
        """
        Load ProfileCheckRules and return a list, grouped by preferences

        :param protocols:
        :return:
        """
        # Try custom credential first
        for c in self.credentials:
            if isinstance(c, CLICredential):
                cli = tuple(set(SUGGEST_CLI).intersection(set(protocols)))
                yield SuggestCLIConfig(
                    protocols=cli,
                    user=c.user,
                    password=c.password or None,
                    super_password=c.super_password or None,
                    raise_privileges=self.raise_privilege,
                )
            elif isinstance(c, SNMPCredential):
                snmp = tuple(set(SUGGEST_SNMP).intersection(set(protocols)))
                yield SuggestSNMPConfig(
                    protocols=snmp,
                    snmp_ro=c.snmp_ro,
                    snmp_rw=c.snmp_rw,
                )
        if self.ignoring_rule:
            return
        ccr: List[CredentialCheckRule] = CredentialCheckRule.objects.filter(is_active=True)
        if self.labels:
            ccr = ccr.filter(
                (m_q(match__labels__in=self.labels, match__exclude_labels__nin=self.labels))
                | m_q(match__labels__exists=False)
            )
        for cc in ccr.read_preference(ReadPreference.SECONDARY_PREFERRED).order_by("preference"):
            # Suggest protocol order
            sp = cc.get_suggest_proto()
            protocol_order = sp or protocols or SUGGEST_PROTOCOLS
            cli = tuple(self.iter_protocols(SUGGEST_CLI, protocols, sp, order=protocol_order))
            snmp = tuple(self.iter_protocols(SUGGEST_SNMP, protocols, sp, order=protocol_order))
            # CLI
            for ap in cc.suggest_auth_profile:
                ap = ap.auth_profile
                if cli and (ap.user or ap.password):
                    yield SuggestCLIConfig(
                        cli,
                        user=ap.user,
                        password=ap.password,
                        super_password=ap.super_password or None,
                        raise_privileges=self.raise_privilege,
                    )
                if snmp and (ap.snmp_ro or ap.snmp_rw):
                    yield SuggestSNMPConfig(
                        snmp,
                        snmp_ro=ap.snmp_ro,
                        snmp_rw=ap.snmp_rw,
                        check_oids=tuple(cc.suggest_snmp_oids or []) or None,
                    )
            if cli:
                for sc in cc.suggest_credential:
                    yield SuggestCLIConfig(
                        cli,
                        user=sc.user,
                        password=sc.password,
                        super_password=sc.super_password or None,
                        raise_privileges=self.raise_privilege,
                    )
            if snmp:
                for ss in cc.suggest_snmp:
                    yield SuggestSNMPConfig(
                        snmp,
                        snmp_ro=ss.snmp_ro,
                        snmp_rw=ss.snmp_rw,
                        check_oids=tuple(cc.suggest_snmp_oids or []) or None,
                    )

    def iter_result(self, protocols: Optional[Iterable[Protocol]] = None) -> List[ProtocolResult]:
        """
        Iterate over suggest result
        :param protocols: List protocols for check
        :return:
        """
        unsupported_proto = set()
        processed = set()
        for suggest in self.iter_suggests(protocols):
            cred = suggest.get_credential()
            for protocol in suggest.protocols:
                if unsupported_proto and protocol in unsupported_proto:
                    # Skip unsupported proto
                    continue
                if (protocol, cred) in processed:
                    # Skip already checked credential
                    continue
                self.logger.debug("Trying suggest: %s:%s", protocol, cred)
                if not hasattr(self, f"do_{suggest.check_method}"):
                    self.logger.info("Unknown check method: %s", suggest.check_method)
                    continue
                check = getattr(self, f"do_{suggest.check_method}")
                p_check: "ProtocolResult" = check(protocol, cred)
                if not p_check.status and self.is_unsupported_error(p_check.error):
                    # Protocol is unsupported, ignored
                    unsupported_proto.add(p_check.protocol)
                processed.add((protocol, cred))
                yield p_check

    def do_snmp_check(self, protocol: Protocol, cred: SNMPCredential) -> ProtocolResult:
        """

        :param protocol:
        :param cred:
        :return:
        """
        for oid in cred.oids or CHECK_OIDS:
            status, message = self.check_oid(oid, cred.snmp_ro, f"{protocol.config.alias}_get")
            if status:
                break
            if not status and not message:
                message = "Nothing value in MIB View"
        # self.logger.info(
        #     "Guessed community: %s, version: %d",
        #     config.snmp_ro,
        #     config.protocol.config.snmp_version,
        # )
        return ProtocolResult(
            protocol=protocol,
            status=status,
            error=message,
            credential=cred,
        )

    def do_cli_check(self, protocol: Protocol, cred: CLICredential) -> ProtocolResult:
        """
        Check suggest CLIT config
        :param protocol:
        :param cred: Credential for Check
        :return:
        """
        if self.ignoring_cli:
            # Skipped
            return ProtocolResult(protocol=protocol, status=True, skipped=True)
        status, message = self.check_login(
            cred.user,
            cred.password,
            cred.super_password,
            protocol=protocol,
            raise_privilege=cred.raise_privilege,
        )
        return ProtocolResult(
            protocol=protocol,
            status=status,
            error=message,
            credential=cred,
        )

    def check_oid(self, oid: str, community: str, version="snmp_v2c_get") -> Tuple[bool, str]:
        """
        Perform SNMP GET. Param is OID or symbolic name, version is activator method
        todo mass check
        :param oid:
        :param community:
        :param version:
        :return:
        """
        self.logger.info(
            "Trying community '%s': %s, version: %s", safe_shadow(community), oid, version
        )
        self.logger.debug("Trying community '%s': %s, version: %s", community, oid, version)
        try:
            result, message = open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).__getattr__(version)(self.address, community, oid, 5, True)
            if message.startswith("<"):
                message = message.strip("<>")
            self.logger.info("Result: %s (%s)", result, message)
            return result is not None, message or ""
        except RPCError as e:
            self.logger.info("RPC Error: %s", e)
            return False, str(e)

    def check_login(
        self,
        user: str,
        password: str,
        super_password: str,
        protocol: Protocol,
        raise_privilege: bool = True,
    ) -> Tuple[bool, str]:
        """
        Check user, password for cli proto
        :param user:
        :param password:
        :param super_password:
        :param protocol:
        :param raise_privilege:
        :return:
        """
        self.logger.debug("Checking %s: %s/%s/%s", protocol, user, password, super_password)
        self.logger.info(
            "Checking %s: %s/%s/%s",
            protocol,
            safe_shadow(user),
            safe_shadow(password),
            safe_shadow(super_password),
        )
        try:
            r = open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).script(
                f"{self.profile}.login",
                {
                    "cli_protocol": protocol.config.alias,
                    "cli_port": self.port,
                    "address": self.address,
                    "user": user,
                    "password": password,
                    "super_password": super_password,
                    "path": None,
                    "raise_privileges": raise_privilege,
                    "access_preference": "C",
                },
            )
            self.logger.info("Result: %s, %s", r, r["message"])
            return bool(r["result"]), r["message"]  # bool(False) == bool(None)
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False, ""

    def get_first(self, protocols: Iterable[Protocol]) -> List[ProtocolResult]:
        """
        Get first result
        :param protocols:
        :return:
        """
        processed_proto = set()
        result = []
        for sr in self.iter_result(protocols):
            if not sr.status and not result:
                # Skip failed result
                continue
            elif (
                result and result[-1].credential != sr.credential and sr.protocol in processed_proto
            ):
                break
            result.append(sr)
            processed_proto.add(sr.protocol)
        return result
