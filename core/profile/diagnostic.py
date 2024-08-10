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
from noc.core.checkers.http import HTTP_DIAG, HTTPS_DIAG
from noc.sa.models.profilecheckrule import ProfileCheckRule, SuggestProfile
from noc.core.wf.diagnostic import DiagnosticConfig
from noc.core.checkers.base import Check, CheckResult


class ProfileDiagnostic:
    """
    Run diagnostic by config and check status
    """

    method_check_map = {
        "http_get": HTTP_DIAG,
        "https_get": HTTPS_DIAG,
    }

    def __init__(
        self,
        cfg: DiagnosticConfig,
        labels: Optional[List[str]] = None,
        logger=None,
        address: Optional[str] = None,
        cred: Optional[Union[SNMPCredential, SNMPv3Credential]] = None,
        **kwargs,
    ):
        self.config = cfg
        self.labels = labels
        self.logger = logger or logging.getLogger("profilediagnostic")
        self.address = address
        self.unsupported_method: Set[str] = set()
        self.snmp_credential = cred
        self.reason: Optional[str] = None
        self.result_cache: Dict[Tuple[str, str], str] = {}
        self.profile: Optional[str] = None
        self.ignoring_snmp = False
        self.profile_checks: List[Tuple[Check, ...]] = []
        self.rules: Dict[Tuple[str, str, int], List[SuggestProfile]] = self.load_rules()

    def iter_checks(self) -> Iterable[Tuple[Check, ...]]:
        for c in self.profile_checks:
            if self.profile:
                break
            yield c

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
                self.result_cache[(method, d.name)] = d.value

    def get_result(
        self, checks: List[CheckResult]
    ) -> Optional[Tuple[Optional[bool], Optional[str], Optional[Dict[str, Any]]]]:
        """Getting Diagnostic result: State and reason"""
        self.parse_checks(checks)
        snmp_result, http_result = "", ""
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
                return True, None, {"profile": rule.profile}
        if snmp_result or http_result:
            error = f"Not find profile for OID: {snmp_result} or HTTP string: {http_result}"
        elif not snmp_result:
            error = "Cannot fetch snmp data, check device for SNMP access"
        elif not http_result:
            error = "Cannot fetch HTTP data, check device for HTTP access"
        self.logger.info("Cannot detect profile: %s", error)
        self.reason = error
        # Data
        return False, self.reason, None

    def load_rules(self) -> Dict[Tuple[str, str, int], List[SuggestProfile]]:
        """
        Convert list to tree: (method, param) -> Rules
        """
        r = defaultdict(list)
        oids = []
        http_checks = []
        snmp_checks = []
        for rule in ProfileCheckRule.get_profile_check_rules():
            r[rule.query_key].append(rule)
            if rule.method == "snmp_v2c_get":
                param = self.clean_snmp_param(rule.param)
                if param not in oids:
                    oids.append(param)
            elif rule.method == "http_get" or rule.method == "https_get":
                c = Check(
                    name=self.method_check_map[rule.method],
                    address=self.address,
                    args={"url": rule.param},
                )
                if c not in http_checks:
                    http_checks.append(c)
        if oids and self.snmp_credential:
            snmp_checks += [
                Check(
                    name=(
                        "SNMPv2c" if isinstance(self.snmp_credential, SNMPCredential) else "SNMPv3"
                    ),
                    address=self.address,
                    credential=self.snmp_credential,
                    args={"oids": ",".join(oids)},
                ),
            ]
        if snmp_checks:
            self.profile_checks += [tuple(snmp_checks)]
        if http_checks:
            self.profile_checks += [tuple(http_checks)]
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
