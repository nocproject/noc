# ----------------------------------------------------------------------
# Credential checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import enum
from dataclasses import dataclass
from typing import Optional, List, Tuple, Union, Set, Iterator

# Third-party modules
import cachetools

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.text import safe_shadow
from noc.sa.models.profile import Profile
from noc.sa.models.authprofile import AuthProfile
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.core.mib import mib

CHECK_OIDS = [
    mib["SNMPv2-MIB::sysObjectID.0"],
    mib["SNMPv2-MIB::sysUpTime.0"],
    mib["SNMPv2-MIB::sysDescr.0"],
]


@dataclass(frozen=True)
class ProtoConfig(object):
    alias: str
    snmp_version: Optional[int] = None
    is_http: bool = False
    is_cli: bool = False


CONFIGS = {
    1: ProtoConfig("telnet", is_cli=True),
    2: ProtoConfig("ssh", is_cli=True),
    3: ProtoConfig("http", is_http=True),
    4: ProtoConfig("https", is_http=True),
    5: ProtoConfig("beef", is_cli=True),
    6: ProtoConfig("snmp_v1", snmp_version=0),
    7: ProtoConfig("snmp_v2c", snmp_version=1),
    8: ProtoConfig("snmp_v3", snmp_version=3),
}


class Protocol(enum.Enum):
    @property
    def config(self):
        return CONFIGS[self.value]

    TELNET = 1
    SSH = 2
    HTTP = 3
    HTTPS = 4
    BEEF = 5
    SNMPv1 = 6
    SNMPv2c = 7
    SNMPv3 = 8


@dataclass(frozen=True)
class SuggestSNMP(object):
    preference: int
    protocols: Tuple[Protocol, ...]
    snmp_ro: Optional[str] = None
    snmp_rw: Optional[str] = None
    check_oids: Optional[Tuple[str, ...]] = None


@dataclass(frozen=True)
class SuggestCLI(object):
    preference: int
    protocols: Tuple[Protocol, ...]
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None


@dataclass(frozen=True)
class SuggestConfig(object):
    preference: int
    check_oids: Optional[Tuple[str, ...]] = None
    protocols: Optional[Tuple[Protocol, ...]] = None


@dataclass
class SuggestResult(object):
    protocols: List[Protocol]
    credential: Union[SuggestSNMP, SuggestCLI]
    error: Optional[str] = None


@dataclass(frozen=True)
class Credential(object):
    protocols: List[Protocol]
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None
    snmp_ro: Optional[str] = None
    snmp_rw: Optional[str] = None
    auth_profile: Optional[AuthProfile] = None


SUGGEST_SNMP: Tuple[Protocol, ...] = (Protocol(7), Protocol(6))
SUGGEST_CLI: Tuple[Protocol, ...] = (Protocol(1), Protocol(2))
SUGGEST_PROTOCOLS: Tuple[Protocol, ...] = SUGGEST_SNMP + SUGGEST_CLI


class CredentialChecker(object):
    base_logger = logging.getLogger("credentialchecker")
    _rules_cache = cachetools.TTLCache(10, ttl=60)

    def __init__(
        self,
        address,
        pool,
        labels: List[str] = None,
        logger=None,
        profile: Optional[str] = None,
        calling_service: str = "credentialchecker",
        protocols: Optional[List[int]] = None,
    ):
        self.address = address
        self.pool = pool
        self.labels = labels
        self.logger = PrefixLoggerAdapter(
            logger or self.base_logger, "%s][%s" % (self.pool or "", self.address or "")
        )
        self.calling_service = calling_service
        self.profile = profile
        self.profile: "Profile" = Profile.get_by_name(profile) if profile else None
        self.protocols: Optional[List[Protocol]] = protocols
        self.ignoring_cli = False
        if self.profile is None or self.profile.is_generic:
            self.logger.error("CLI Access for Generic profile is not supported. Ignoring")
            self.ignoring_cli = True
        # Credential
        self.auth_profiles: Set[AuthProfile] = set()
        self.result: List[SuggestResult] = []

    @staticmethod
    def merge_protocols(*args, order: Tuple[Protocol, ...] = None):
        return tuple(
            sorted(
                set(args[0]).intersection(*[set(s) for s in args[1:] if s]),
                key=lambda x: order.index(x),
            )
        )

    def iter_suggests(
        self, protocols: Tuple[Protocol, ...] = None
    ) -> Iterator[Union[SuggestCLI, SuggestSNMP]]:
        """
        Load ProfileCheckRules and return a list, grouped by preferences

        :param protocols:
        :return:
        """
        r = set()
        auth_profiles = set()
        ccr: List[CredentialCheckRule] = CredentialCheckRule.objects.filter()
        if self.labels:
            ccr = ccr.filter(match__labels__in=self.labels)
        for cc in ccr.order_by("preference"):
            sp = cc.suggest_protocols or protocols or SUGGEST_PROTOCOLS
            cli_protocols = self.merge_protocols(
                SUGGEST_CLI, protocols, cc.suggest_protocols, self.protocols, order=sp
            )
            snmp_protocols = self.merge_protocols(
                SUGGEST_SNMP, protocols, cc.suggest_protocols, self.protocols, order=sp
            )
            for ap in cc.suggest_auth_profile:
                ap = ap.auth_profile
                if ap in auth_profiles:
                    self.logger.info("Authentication profile already processed. Skipping.")
                    continue
                auth_profiles.add(ap)
                # self.auth_profiles.add(ap)
                if (ap.user or ap.password) and cli_protocols:
                    sc = SuggestCLI(
                        cc.preference,
                        cli_protocols,
                        user=ap.user,
                        password=ap.password,
                        super_password=ap.super_password,
                    )
                    if sc not in r:
                        yield sc
                    r.add(sc)
                if (ap.snmp_ro or ap.snmp_rw) and snmp_protocols:
                    ss = SuggestSNMP(
                        cc.preference, snmp_protocols, snmp_ro=ap.snmp_ro, snmp_rw=ap.snmp_rw
                    )
                    if ss not in r:
                        yield ss
                    r.add(ss)
            if snmp_protocols:
                for ss in cc.suggest_snmp:
                    ss = SuggestSNMP(
                        cc.preference, snmp_protocols, snmp_ro=ss.snmp_ro, snmp_rw=ss.snmp_rw
                    )
                    if ss not in r:
                        yield ss
                    r.add(ss)
            if cli_protocols:
                for sc in cc.suggest_credential:
                    sc = SuggestCLI(
                        cc.preference,
                        snmp_protocols,
                        user=sc.user,
                        password=sc.password,
                        super_password=sc.super_password,
                    )
                    if sc not in r:
                        yield sc
                    r.add(sc)
        return r

    def do_snmp_check(self):
        """

        :return:
        """
        for suggest in self.iter_suggests(SUGGEST_SNMP):
            s_result = SuggestResult(protocols=[], credential=suggest)
            for oid in suggest.check_oids or CHECK_OIDS:
                for proto in suggest.protocols:
                    if self.check_oid(oid, suggest.snmp_ro, f"{proto.config.alias}_get"):
                        self.logger.info(
                            "Guessed community: %s, version: %d",
                            suggest.snmp_ro,
                            proto.config.snmp_version,
                        )
                        s_result.protocols.append(proto)
                if s_result.protocols:
                    self.result.append(s_result)
                    break
            if s_result.protocols:
                break

    @staticmethod
    def is_unsupported_error(message) -> bool:
        if "Exception: TimeoutError()" in message:
            return True
        return False

    def do_cli_check(self):
        """
        Iter CLI Credential
        :return: user, password, enable_password
        """
        if self.ignoring_cli:
            return
        refused_proto = set()
        for suggest in self.iter_suggests(SUGGEST_CLI):
            s_result = SuggestResult(protocols=[], credential=suggest)
            for proto in suggest.protocols:
                if proto in refused_proto:
                    continue
                result, message = self.check_login(
                    suggest.user, suggest.password, suggest.super_password, protocol=proto
                )
                if result:
                    s_result.protocols.append(proto)
                elif self.is_unsupported_error(message):
                    refused_proto.add(proto)
            if s_result.protocols:
                self.result.append(s_result)
                break

    def check_oid(self, oid: str, community: str, version="snmp_v2c_get"):
        """
        Perform SNMP GET. Param is OID or symbolic name, version is activator method
        todo mass check
        :param oid:
        :param community:
        :param version:
        :return:
        """
        self.logger.info("Trying community '%s': %s, version: %s", community, oid, version)
        try:
            r = open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).__getattr__(version)(self.address, community, oid)
            self.logger.info("Result: %s", r)
            return r is not None
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False

    def check_login(self, user: str, password: str, super_password: str, protocol: Protocol):
        """
        Check user, password for cli proto
        :param user:
        :param password:
        :param super_password:
        :param protocol:
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
                    "address": self.address,
                    "user": user,
                    "password": password,
                    "super_password": super_password,
                    "path": None,
                    "raise_privileges": "E",
                    "access_preference": "C",
                },
            )
            self.logger.info("Result: %s, %s", r, r["message"])
            return bool(r["result"]), r["message"]  # bool(False) == bool(None)
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False, ""

    def get_auth_profile(self, credential: Credential) -> Optional[AuthProfile]:
        """
        Find Auth Profile for suggest credential
        :return:
        """
        # Combination suggest for auth_profile
        for ap in self.auth_profiles:
            if (
                ap.snmp_ro == credential.snmp_ro
                and ap.user == credential.user
                and ap.password == credential.password
                and ap.super_password == credential.super_password
            ):
                return ap

    def get_credential(self) -> Optional[Credential]:
        """
        Return Address Credential
        :return:
        """
        if not self.result:
            return
        protocols = []
        snmp_ro, snmp_rw = None, None
        user, password, super_password = None, None, None
        for sc in self.result:
            if set(SUGGEST_SNMP).intersection(set(sc.protocols)):
                protocols += list(sc.protocols)
                snmp_ro = sc.credential.snmp_ro
                snmp_rw = sc.credential.snmp_rw
            if set(SUGGEST_CLI).intersection(set(sc.protocols)):
                protocols += list(sc.protocols)
                user = sc.credential.user
                password = sc.credential.password
                super_password = sc.credential.super_password
        return Credential(
            protocols=protocols,
            user=user,
            password=password,
            super_password=super_password,
            snmp_ro=snmp_ro,
            snmp_rw=snmp_rw,
        )