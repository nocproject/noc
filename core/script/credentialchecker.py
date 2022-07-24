# ----------------------------------------------------------------------
# Credentail checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import enum
from dataclasses import dataclass
from typing import Optional, List, Tuple, Iterator, Set, Dict, Union
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
class SuggestSNMP(object):
    snmp_ro: Optional[str] = None
    snmp_rw: Optional[str] = None
    check_oids: List[str] = None


@dataclass(frozen=True)
class SuggestCLI(object):
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None


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


SUGGEST_PROTOCOLS = [1, 2, 7, 6]


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
        self.protocols: Optional[List[Protocol]] = [
            Protocol(p_num) for p_num in SUGGEST_PROTOCOLS if not protocols or p_num in protocols
        ]
        self.ignoring_cli = False
        if self.profile is None or self.profile.is_generic:
            self.logger.error("CLI Access for Generic profile is not supported. Ignoring")
            self.ignoring_cli = True
        # Credential
        self.snmp_ro: Optional[str] = None
        self.snmp_rw: Optional[str] = None
        self.user: Optional[str] = None
        self.password: Optional[str] = None
        self.super_password: Optional[str] = None
        self.auth_profile: Optional[AuthProfile] = None
        self.auth_profiles: List[AuthProfile] = []

    def set_credential(
        self,
        snmp_ro: Optional[str] = None,
        snmp_rw: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        super_password: Optional[str] = None,
        auth_profile: Optional[str] = None,
    ):
        self.logger.info("Setting credentials")
        if snmp_ro:
            self.snmp_ro = snmp_ro
        if snmp_rw:
            self.snmp_rw = snmp_rw
        if user:
            self.user = user
        if password:
            self.password = password
        if super_password:
            self.super_password = super_password

    def get_rules(self) -> Dict[Tuple[int, List[Protocol]], List[Union[SuggestCLI, SuggestSNMP]]]:
        """
        preference -> proto -> list[Credential]
        Load ProfileCheckRules and return a list, grouped by preferences
        [{
            (method, param) -> [(
                    match_method,
                    value,
                    action,
                    profile,
                    rule_name
                ), ...]

        }]
        """
        r = defaultdict(list)
        for cc in CredentialCheckRule.objects.filter():
            cc: "CredentialCheckRule"
            for ap in cc.suggest_auth_profile:
                ap = ap.auth_profile
                if ap.user or ap.password:
                    r[cc.preference, (Protocol(1), Protocol(2))] += [
                        SuggestCLI(
                            user=ap.user, password=ap.password, super_password=ap.super_password
                        )
                    ]
                if ap.snmp_ro or ap.snmp_rw:
                    r[cc.preference, (Protocol(6), Protocol(7))] += [
                        SuggestSNMP(snmp_ro=ap.snmp_ro, snmp_rw=ap.snmp_rw)
                    ]
                self.auth_profiles.append(ap)
            for ss in cc.suggest_snmp:
                r[cc.preference, (Protocol(6), Protocol(7))] += [
                    SuggestSNMP(snmp_ro=ss.snmp_ro, snmp_rw=ss.snmp_rw)
                ]
            for sc in cc.suggest_credential:
                r[cc.preference, (Protocol(1), Protocol(2))] += [
                    SuggestCLI(user=sc.user, password=sc.password, super_password=sc.super_password)
                ]
        return r

    def iter_snmp(self) -> None:
        """

        for oid in self.CHECK_OIDS:
            for (ro, rw) in self.object.auth_profile.iter_snmp():
                for ver in sorted(self.CHECK_VERSION):
                    if self.check_oid(oid, ro, self.CHECK_VERSION[ver]):
                        self.logger.info("Guessed community: %s, version: %d", ro, ver)
                        self.object._suggest_snmp = (ro, rw, self.CHECK_VERSION[ver])
                        if self.object.get_access_preference() == "S":
                            self.set_credentials(snmp_ro=ro, snmp_rw=rw)
                        return
        :return: snmp_ro, snmp_rw
        """
        d = self.get_rules()
        for proto in sorted(d, key=lambda x: x[0]):
            if Protocol(6) not in proto[1]:
                self.logger.info("Skipping proto")
                continue
            checked_cred = False
            for cred in d[proto]:
                if checked_cred:
                    break
                for ver in proto[1]:
                    if self.check_oid(CHECK_OIDS[0], cred.snmp_ro, f"{ver.config.alias}_get"):
                        self.logger.info(
                            "Guessed community: %s, version: %d",
                            cred.snmp_ro,
                            ver.config.snmp_version,
                        )
                        checked_cred = True
                        # self.set_credential()

    def iter_cli(self) -> Tuple[str, str, str]:
        """
        Iter CLI Credential
        :return: user, password, enable_password
        """
        yield

    def get_snmp_credentials(self):
        """
        Return SNMP Credential
        :return:
        """
        ...

    def get_cli_credential(self):
        """
        Return CLI Credential
        :return: proto, credential, raise_privilege. From proto -> diagnostic
        """

        ...

    def check_oid(self, oid: str, community: str, version="snmp_v2c_get"):
        """
        Perform SNMP v2c GET. Param is OID or symbolic name
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
                    # "raise_privileges": self.object.to_raise_privileges,
                    # "access_preference": self.object.get_access_preference(),
                },
            )
            self.logger.info("Result: %s, %s", r, r["message"])
            return bool(r["result"]), r["message"]  # bool(False) == bool(None)
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False, ""
