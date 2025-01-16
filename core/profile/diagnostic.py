# ----------------------------------------------------------------------
# Profile diagnostic
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from collections import defaultdict
from typing import List, Iterable, Optional, Tuple, Union, Dict, Set, Any

# NOC modules
from noc.core.mib import mib
from noc.core.script.scheme import SNMPCredential, SNMPv3Credential
from noc.core.wf.diagnostic import HTTP_DIAG, HTTPS_DIAG
from noc.sa.models.profilecheckrule import ProfileCheckRule, SuggestProfile
from noc.core.wf.diagnostic import DiagnosticConfig, CheckStatus
from noc.core.checkers.base import Check, CheckResult


class ProfileDiagnostic:
    """
    Run diagnostic by config and check status
    """

    method_check_map = {
        "http_get": HTTP_DIAG,
        "https_get": HTTPS_DIAG,
    }

    def __init__(self, config: DiagnosticConfig, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger("profilediagnostic")
        self.unsupported_method: Set[str] = set()
        self.reason: Optional[str] = None
        self.result_cache: Dict[Tuple[str, str], str] = {}
        self.profile: Optional[str] = None
        self.ignoring_snmp = False
        self.oids = []
        self.urls = []
        self.rules: Dict[Tuple[str, str, int], List[SuggestProfile]] = self.load_rules()

    def iter_checks(
        self,
        address: str,
        labels: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        cred: Optional[Union[SNMPCredential, SNMPv3Credential]] = None,
        **kwargs,
    ) -> Iterable[Tuple[Check, ...]]:
        if not cred:
            self.ignoring_snmp = True
        if self.oids and cred and isinstance(cred, SNMPCredential):
            yield (
                Check(
                    name="SNMPv2c",
                    address=address,
                    credential=cred,
                    args={"oids": ",".join(self.oids)},
                ),
            )
        elif self.oids and cred and isinstance(cred, SNMPv3Credential):
            yield (
                Check(
                    name="SNMPv3",
                    address=address,
                    credential=cred,
                    args={"oids": ",".join(self.oids)},
                ),
            )
        if self.profile or not self.urls:
            return
        yield tuple(
            Check(name=self.method_check_map[m], address=address, args={"url": url})
            for (m, url) in self.urls
        )

    def parse_checks(self, checks: List[CheckResult]):
        """Update checks data"""
        for c in checks:
            if c.check.startswith("SNMP"):
                method = "snmp_v2c_get"
            else:
                method = {HTTP_DIAG: "http_get", HTTPS_DIAG: "https_get"}[c.check]
            if not c.status:
                self.unsupported_method.add(method)
                continue
            for d in c.data:
                self.logger.info("[%s] Getting %s, Result: %s", method, d.name, d.value)
                self.result_cache[(method, d.name)] = d.value

    def get_result(
        self, checks: List[CheckResult]
    ) -> Optional[
        Tuple[Optional[bool], Optional[str], Optional[Dict[str, Any]], List[CheckStatus]]
    ]:
        """Getting Diagnostic result: State and reason"""
        self.parse_checks(checks)
        if not self.result_cache:
            error = "Cannot fetch any data for detect Profile. Check Device Access"
        elif "snmp_v2c_get" in self.unsupported_method:
            error = "Cannot fetch snmp data, check device for SNMP access"
        elif "http_get" in self.unsupported_method:
            error = "Cannot fetch HTTP data, check device for HTTP access"
        else:
            error = None
        for method, param, pref in sorted(self.rules, key=lambda x: x[2]):
            if method == "snmp_v2c_get":
                r_key = (method, self.clean_snmp_param(param))
            else:
                r_key = (method, param)
            if method in self.unsupported_method:
                continue
            if r_key in self.result_cache:
                self.logger.debug("Using cached value")
                result = self.result_cache[r_key]
            else:
                continue
            rule = self.find_profile((method, param, pref), result)
            if rule:
                self.logger.info("Matched profile: %s (%s)", rule.profile, rule.name)
                # @todo: process MAYBE rule
                self.profile = rule.profile
                return True, None, {"profile": rule.profile}, []
            else:
                error = f"Not find profile for OID or HTTP string: {result}"
        self.logger.info("Cannot detect profile: %s", error)
        self.reason = error
        # Data
        return False, self.reason, None, []

    def load_rules(self) -> Dict[Tuple[str, str, int], List[SuggestProfile]]:
        """
        Convert list to tree: (method, param) -> Rules
        """
        r = defaultdict(list)
        for rule in ProfileCheckRule.get_profile_check_rules():
            r[rule.query_key].append(rule)
            if rule.method == "snmp_v2c_get":
                param = self.clean_snmp_param(rule.param)
                if param not in self.oids:
                    self.oids.append(param)
            elif rule.method == "http_get" or rule.method == "https_get":
                if rule.param not in self.urls:
                    self.urls.append((rule.method, rule.param))
        return r

    def find_profile(self, key, result: str) -> Optional[SuggestProfile]:
        if key not in self.rules:
            self.logger.warning("Not find rule for method: %s", key)
            return
        for rule in self.rules[key]:
            if rule.is_match(result):
                return rule

    def clean_snmp_param(self, param):
        try:
            param = mib[param]
        except KeyError:
            self.logger.error("Cannot resolve OID '%s'. Ignoring", param)
            return
        return param

    def get_profile(self) -> Tuple[Optional[str], Optional[str]]:
        unsupported_method = set()
        snmp_result, http_result = "", ""
        for method, param, pref in sorted(self.rules, key=lambda x: x[2]):
            if method == "snmp_v2c_get":
                r_key = (method, self.clean_snmp_param(param))
            else:
                r_key = (method, param)
            if method in unsupported_method:
                continue
            if r_key in self.result_cache:
                self.logger.debug("Using cached value")
                result = self.result_cache[r_key]
            else:
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
