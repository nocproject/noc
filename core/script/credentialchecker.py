# ----------------------------------------------------------------------
# Credentail checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import enum
import operator
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Union
from collections import defaultdict

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
    snmp_ro: Optional[str] = None
    snmp_rw: Optional[str] = None


@dataclass(frozen=True)
class SuggestCLI(object):
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None


@dataclass(frozen=True)
class SuggestConfig(object):
    preference: int
    check_oids: Optional[Tuple[str, ...]] = None
    protocols: Optional[Tuple[Protocol, ...]] = None


SUGGEST_SNMP: Tuple[Protocol, ...] = (Protocol(7), Protocol(6))
SUGGEST_CLI: Tuple[Protocol, ...] = tuple(p for p in Protocol if p.config.is_cli)
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
        self.snmp_credential: Optional[SuggestSNMP] = None
        self.cli_credential: Optional[SuggestCLI] = None
        self.auth_profiles: List[AuthProfile] = []

    def set_credential(self, credential: Union[SuggestCLI, SuggestSNMP]):
        self.logger.info("Setting credentials")
        if isinstance(credential, SuggestSNMP):
            self.snmp_credential = credential
        elif isinstance(credential, SuggestCLI):
            self.cli_credential = credential

    def get_rules(
        self, protocols: Tuple[Protocol, ...] = None
    ) -> Dict[SuggestConfig, List[Union[SuggestCLI, SuggestSNMP]]]:
        """
        Load ProfileCheckRules and return a list, grouped by preferences

        :param protocols:
        :return:
        """
        r = defaultdict(list)
        for cc in CredentialCheckRule.objects.filter():
            cc: "CredentialCheckRule"
            sp = cc.suggest_protocols or protocols or SUGGEST_PROTOCOLS
            cli_protocols = tuple(
                sorted(
                    set(SUGGEST_CLI).intersection(
                        *[set(s) for s in [protocols, cc.suggest_protocols, self.protocols] if s]
                    ),
                    key=lambda x: sp.index(x),
                )
            )
            snmp_protocols = tuple(
                sorted(
                    set(SUGGEST_SNMP).intersection(
                        *[set(s) for s in [protocols, cc.suggest_protocols, self.protocols] if s]
                    ),
                    key=lambda x: sp.index(x),
                )
            )
            scc = SuggestConfig(preference=cc.preference, protocols=cli_protocols)
            scs = SuggestConfig(preference=cc.preference, protocols=snmp_protocols)
            for ap in cc.suggest_auth_profile:
                ap = ap.auth_profile
                if (ap.user or ap.password) and cli_protocols:
                    sc = SuggestCLI(
                        user=ap.user, password=ap.password, super_password=ap.super_password
                    )
                    if sc not in r[scc]:
                        r[scc] += [sc]
                if (ap.snmp_ro or ap.snmp_rw) and snmp_protocols:
                    ss = SuggestSNMP(snmp_ro=ap.snmp_ro, snmp_rw=ap.snmp_rw)
                    if ss not in r[scs]:
                        r[scs] += [ss]
                self.auth_profiles.append(ap)
            if snmp_protocols:
                for ss in cc.suggest_snmp:
                    ss = SuggestSNMP(snmp_ro=ss.snmp_ro, snmp_rw=ss.snmp_rw)
                    if ss not in r[scs]:
                        r[scs] += [ss]
            if cli_protocols:
                for sc in cc.suggest_credential:
                    sc = SuggestCLI(
                        user=sc.user, password=sc.password, super_password=sc.super_password
                    )
                    if sc not in r[scc]:
                        r[scc] += [sc]
        return r

    def do_snmp_check(self):
        """

        :return:
        """
        d = self.get_rules(SUGGEST_SNMP)
        checked_cred = False
        for config in sorted(d, key=operator.attrgetter("preference")):
            for cred in d[config]:
                for proto in config.protocols:
                    if self.check_oid(CHECK_OIDS[0], cred.snmp_ro, f"{proto.config.alias}_get"):
                        self.logger.info(
                            "Guessed community: %s, version: %d",
                            cred.snmp_ro,
                            proto.config.snmp_version,
                        )
                        checked_cred = True
                        self.snmp_credential = cred
                if checked_cred:
                    break
            if checked_cred:
                break

    def do_cli_check(self):
        """
        Iter CLI Credential
        :return: user, password, enable_password
        """
        if self.ignoring_cli:
            return
        d = self.get_rules(SUGGEST_CLI)
        checked_cred = False
        for config in sorted(d, key=operator.attrgetter("preference")):
            for proto in config.protocols:
                for cred in d[config]:
                    result, message = self.check_login(
                        cred.user, cred.password, cred.super_password, protocol=proto
                    )
                    if result:
                        checked_cred = True
                        self.cli_credential = cred
                        break
            if checked_cred:
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
        self.logger.debug("Checking %s/%s/%s", user, password, super_password)
        self.logger.info(
            "Checking %s/%s/%s",
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

    def get_auth_profile(self) -> Optional[AuthProfile]:
        """
        Find Auth Profile for suggest credential
        :return:
        """
        for ap in self.auth_profiles:
            if (
                ap.snmp_ro == self.snmp_credential.snmp_ro
                and ap.user == self.cli_credential.user
                and ap.password == self.cli_credential.password
                and ap.super_password == self.cli_credential.super_password
            ):
                return ap

    def get_snmp_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Return SNMP Credential
        :return:
        """
        return self.snmp_credential.snmp_ro, self.snmp_credential.snmp_rw

    def get_cli_credential(self):
        """
        Return CLI Credential
        :return: proto, credential, raise_privilege. From proto -> diagnostic
        """
        return self.cli_credential
