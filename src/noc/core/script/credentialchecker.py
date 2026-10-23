# ----------------------------------------------------------------------
# Credential checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from collections.abc import Iterator, Iterable

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
class SNMPCredential:
    snmp_ro: str | None = None
    snmp_rw: str | None = None
    oids: list[str] | None = None


@dataclass(frozen=True)
class CLICredential:
    user: str | None = None
    password: str | None = None
    super_password: str | None = None
    raise_privilege: bool = True


@dataclass(frozen=True)
class SuggestSNMPConfig:
    protocols: tuple[Protocol, ...]
    check_method: str = "snmp_check"
    snmp_ro: str | None = None
    snmp_rw: str | None = None
    check_oids: tuple[str, ...] | None = None

    def get_credential(self) -> SNMPCredential:
        return SNMPCredential(self.snmp_ro, self.snmp_rw, oids=self.check_oids)


@dataclass(frozen=True)
class SuggestCLIConfig:
    protocols: tuple[Protocol, ...]
    check_method: str = "cli_check"
    user: str | None = None
    password: str | None = None
    super_password: str | None = None
    raise_privileges: bool = True
    access_preference: str | None = "C"

    def get_credential(self) -> CLICredential:
        return CLICredential(
            user=self.user,
            password=self.password,
            super_password=self.super_password,
            raise_privilege=self.raise_privileges,
        )


@dataclass(frozen=True)
class ProtocolResult:
    protocol: Protocol
    status: bool
    skipped: bool = False
    error: str | None = None
    credential: CLICredential | SNMPCredential | None = None


SUGGEST_SNMP: tuple[Protocol, ...] = (Protocol(7), Protocol(6))
SUGGEST_CLI: tuple[Protocol, ...] = (Protocol(1), Protocol(2))
SUGGEST_PROTOCOLS: tuple[Protocol, ...] = SUGGEST_SNMP + SUGGEST_CLI


class CredentialChecker:
    """Credential checker for CLI/SNMP credential. Allow suggests credential"""

    base_logger = logging.getLogger("credentialchecker")

    def __init__(
        self,
        address,
        pool,
        labels: list[str] | None = None,
        port: str | None = None,
        logger=None,
        profile: str | None = None,
        raise_privilege: bool = True,
        calling_service: str = "credentialchecker",
        credentials: list[SuggestCLIConfig | SuggestSNMPConfig] | None = None,
        ignoring_rule: bool = False,
    ):
        """
        Args:
            address: Device IP address
            pool: Activator pool for request
            labels: List labels for filter CredentialCheck Rules
            logger: logging instance
            profile: SA Profile
            raise_privilege: Try raise privilege for check
            calling_service: Service name
            credentials: Custom credential for check
            ignoring_rule: Do not use rule for suggest credential
        """
        self.address = address
        self.pool = pool
        self.port = port
        self.labels = labels
        self.logger = PrefixLoggerAdapter(
            logger or self.base_logger, f"{self.pool or ''}][{self.address or ''}"
        )
        self.calling_service = calling_service
        self.profile: "Profile" | None = profile
        if isinstance(self.profile, str):
            self.profile = Profile.get_by_name(profile) if profile else None
        self.credentials: list[CLICredential | SNMPCredential] = credentials or []
        self.ignoring_rule = ignoring_rule
        self.ignoring_cli = False
        self.raise_privilege = raise_privilege
        if self.profile is None or self.profile.is_generic:
            self.logger.info("CLI Access for Generic profile is not supported. Ignoring")
            self.ignoring_cli = True

    @staticmethod
    def iter_protocols(*args, order: tuple[Protocol, ...] | None = None) -> Iterable[Protocol]:
        """
        Args:
            *args
            order
        """
        yield from sorted(
            set(args[0]).intersection(*[set(s) for s in args[1:] if s]),
            key=lambda x: order.index(x),
        )

    @staticmethod
    def is_unsupported_error(message) -> bool:
        """Todo replace to error_code

        Args:
            message
        """
        if "Exception: TimeoutError()" in message:
            return True
        if "Error: Connection refused" in message:
            return True
        if "Error: Connection reset" in message:
            return True
        return "No supported authentication methods" in message

    def iter_suggests(
        self, protocols: tuple[Protocol, ...] | None = None
    ) -> Iterator[SuggestCLIConfig | SuggestSNMPConfig]:
        """Load ProfileCheckRules and return a list, grouped by preferences

        Args:
            protocols
        """
        # Try custom credential first
        ordered_cli, ordered_snmp = [], []
        for p in protocols:
            if p in SUGGEST_CLI:
                ordered_cli.append(p)
            elif p in SUGGEST_SNMP:
                ordered_snmp.append(p)
        for c in self.credentials:
            if isinstance(c, CLICredential):
                yield SuggestCLIConfig(
                    protocols=tuple(ordered_cli),
                    user=c.user,
                    password=c.password or None,
                    super_password=c.super_password or None,
                    raise_privileges=self.raise_privilege,
                )
            elif isinstance(c, SNMPCredential):
                yield SuggestSNMPConfig(
                    protocols=tuple(ordered_snmp),
                    snmp_ro=c.snmp_ro,
                    snmp_rw=c.snmp_rw,
                )
        if self.ignoring_rule:
            return
        ccr: list[CredentialCheckRule] = CredentialCheckRule.objects.filter(is_active=True)
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

    def iter_result(self, protocols: Iterable[Protocol] | None = None) -> list[ProtocolResult]:
        """Iterate over suggest result

        Args:
            protocols: List protocols for check
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
        Args:
            protocol
            cred
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
        """Check suggest CLIT config

        Args:
            protocol
            cred: Credential for Check
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

    def check_oid(self, oid: str, community: str, version="snmp_v2c_get") -> tuple[bool, str]:
        """Perform SNMP GET. Param is OID or symbolic name, version is activator method
        todo mass check

        Args:
            oid
            community
            version
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
    ) -> tuple[bool, str]:
        """Check user, password for cli proto

        Args:
            user
            password
            super_password
            protocol
            raise_privilege
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

    def get_first(self, protocols: Iterable[Protocol]) -> list[ProtocolResult]:
        """Get first result

        Args:
            protocols
        """
        processed_proto = set()
        result = []
        for sr in self.iter_result(protocols):
            if not sr.status and not result:
                # Skip failed result
                continue
            if result and result[-1].credential != sr.credential and sr.protocol in processed_proto:
                break
            result.append(sr)
            processed_proto.add(sr.protocol)
        return result
