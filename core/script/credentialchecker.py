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
from typing import Optional, Dict, List, Tuple

# Third-party modules
import cachetools

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.text import safe_shadow
from noc.sa.models.profile import Profile
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


SUGGEST_PROTOCOLS = [1, 2, 7, 6]


class CredentialChecker(object):
    base_logger = logging.getLogger("credentialchecker")
    _rules_cache = cachetools.TTLCache(10, ttl=60)

    def __init__(
        self,
        address,
        pool,
        labels: List[str] = None,
        logger: Optional[logging.root] = None,
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

    def iter_snmp(self) -> Tuple[str, str]:
        """
        Iter SNMP Credential
        :return: snmp_ro, snmp_rw
        """
        yield

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
