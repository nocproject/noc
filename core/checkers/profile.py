# ----------------------------------------------------------------------
# Profile checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import operator
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Iterable, Optional, Tuple, Literal, ClassVar, Dict

# Third-party modules
import cachetools

# NOC modules
from noc.core.text import filter_non_printable
from noc.core.mib import mib
from noc.core.script.scheme import SNMPCredential, Protocol
from noc.core.error import NOCError
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from .base import Checker, CheckResult, DataItem, CheckError


@dataclass(frozen=True)
class SuggestProfile(object):
    method: Literal["snmp_v2c_get", "http_get", "https_get"]
    param: str
    match: Literal["eq", "contains", "re"]
    value: str
    profile: str
    preference: int
    name: Optional[str] = None

    _re_cache: ClassVar[Dict[str, str]] = {}

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_re_cache"))
    def get_re(cls, regexp):
        return re.compile(regexp)

    def is_match(self, result: str) -> bool:
        """
        Returns True when result matches value
        """
        if self.match == "eq":
            return result == self.value
        elif self.match == "contains":
            return self.value in result
        elif self.match == "re":
            return bool(self.get_re(self.value).search(result))
        else:
            # self.logger.error("Invalid match method '%s'. Ignoring", self.method)
            return False

    @property
    def query_key(self):
        return self.method, self.param, self.preference


class ProfileChecker(Checker):
    """
    Check ManagedObject profile by rules
    """

    name = "profile"
    CHECKS: List[str] = ["PROFILE"]
    USER_DISCOVERY_USE = False
    SNMP_TIMEOUT_SEC = 5
    PARAMS = ["rules"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "rules" not in kwargs:
            raise AttributeError("Required check rules for works")
        self.rules: Dict[Tuple[str, str, int], List[SuggestProfile]] = self.load_rules(
            kwargs["rules"]
        )

    @staticmethod
    def load_rules(rules: List[SuggestProfile]) -> Dict[Tuple[str, str, int], List[SuggestProfile]]:
        """
        Convert list to tree: (method, param) -> Rules
        """
        r = defaultdict(list)
        for rule in rules:
            r[rule.query_key].append(rule)
        return r

    def iter_result(self, checks) -> Iterable[CheckResult]:
        check = checks[0]
        profile, error = self.get_profile(
            check.address or self.address,
            check.snmp_credential,
        )
        if profile:
            # Skipped
            yield CheckResult(
                check="PROFILE",
                status=bool(profile),
                data=[DataItem(name="profile", value=profile)],
            )
            return
        yield CheckResult(
            check="PROFILE",
            status=bool(profile),
            error=CheckError(code="0", message=filter_non_printable(error)[:200]),
        )
        # If check SNMP failed - Set SNMP error
        # if not checker.ignoring_snmp and checker.snmp_check is False:
        #     for sv in snmp_version:
        #         yield CheckResult(
        #             check={SNMP_v1: "SNMPv1", SNMP_v2c: "SNMPv2c"}[sv],
        #             status=False,
        #             error="Not getting OID on Profile Discovery",
        #         )

    def find_profile(self, key, result: str) -> Optional[SuggestProfile]:
        if key not in self.rules:
            self.logger.warning("Not find rule for method: %s", key)
            return
        for rule in self.rules[key]:
            if rule.is_match(result):
                return rule

    def get_profile(self, address, cred) -> Tuple[Optional[str], Optional[str]]:
        result_cache: Dict[Tuple[str, str], str] = {}
        unsupported_method = set()
        snmp_result, http_result = "", ""
        for method, param, pref in sorted(self.rules, key=lambda x: x[2]):
            r_key = (method, param)
            if method in unsupported_method:
                continue
            if r_key in result_cache:
                self.logger.debug("Using cached value")
                result = result_cache[r_key]
            else:
                try:
                    result = self.do_check(method, param, address, credential=cred)
                except NOCError as e:
                    unsupported_method.add(method)
                    error = str(e)
                    self.logger.error("[%s] Error when doing check: %s", method, error)
                    self.logger.warning("Add method: %s to unsupported", method)
                    continue
            result_cache[r_key] = result
            if not result:
                continue
            rule = self.find_profile((method, param, pref), result)
            if rule:
                self.logger.info("Matched profile: %s (%s)", rule.profile, rule.name)
                # @todo: process MAYBE rule
                return rule.profile, None
        if snmp_result or http_result:
            error = f"Not find profile for OID: {snmp_result} or HTTP string: {http_result}"
        elif not snmp_result:
            error = "Cannot fetch snmp data, check device for SNMP access"
        elif not http_result:
            error = "Cannot fetch HTTP data, check device for HTTP access"
        self.logger.info("Cannot detect profile: %s", error)
        return None, error

    def do_check(
        self, method: str, param: str, address, credential: Optional[SNMPCredential]
    ) -> Optional[str]:
        """
        Perform check
        """
        self.logger.debug("do_check(%s, %s)", method, param)
        h = getattr(self, f"check_{method}", None)
        if not h:
            self.logger.error("Invalid check method '%s'. Ignoring", method)
            return None
        result = h(address, param, credential)
        return result

    def check_snmp_v2c_get(
        self, address: str, param: str, credential: Optional[SNMPCredential] = None
    ) -> Optional[str]:
        """
        Perform SNMP v2c GET. Param is OID or symbolic name
        """
        try:
            param = mib[param]
        except KeyError:
            self.logger.error("Cannot resolve OID '%s'. Ignoring", param)
            return None
        if not credential:
            raise NOCError(msg="Not credential for check")
        snmp_community = credential.snmp_ro
        if credential.snmp_v1_only:
            snmp_version = [Protocol(6)]
        else:
            snmp_version = [Protocol(7), Protocol(6)]
        for p in snmp_version:
            # if v not in {SNMP_v1, SNMP_v2c}:
            #    raise NOCError(msg="Unsupported SNMP version")
            self.logger.info("%s GET: %s", p.name, param)
            try:
                r, message = open_sync_rpc(
                    "activator", pool=self.pool, calling_service=self.calling_service
                ).__getattr__(f"{p.config.alias}_get")(
                    address, snmp_community, param, self.SNMP_TIMEOUT_SEC, True
                )
            except RPCError as e:
                self.logger.error("RPC Error: %s", e)
                return None
            if not r and not message:
                return
            if r:
                return r

    def check_http_get(
        self, address: str, param: str, credential=None, use_https: bool = False
    ) -> Optional[str]:
        """
        Perform HTTP GET check. Param can be URL path or :<port>/<path>
        """
        url = f"http://{address}{param}"
        if use_https:
            url = f"https://{address}{param}"
        self.logger.info("HTTP Request: %s", url)
        try:
            return open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).http_get(url, True)
        except RPCError as e:
            self.logger.error("RPC Error: %s", e)
            return None

    def check_https_get(self, address, param, credential=None):
        """
        Perform HTTPS GET check. Param can be URL path or :<port>/<path>
        """
        self.check_http_get(address, param, credential=credential, use_https=True)
