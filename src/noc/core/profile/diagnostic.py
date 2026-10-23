# ----------------------------------------------------------------------
# Profile diagnostic
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from collections import defaultdict
from collections.abc import Iterable

# NOC modules
from noc.core.mib import mib
from noc.core.script.scheme import SNMPCredential, SNMPv3Credential
from noc.core.diagnostic.hub import HTTP_DIAG, HTTPS_DIAG
from noc.core.models.inputsources import InputSource
from noc.sa.models.profilecheckrule import ProfileCheckRule, SuggestProfile
from noc.core.diagnostic.types import DiagnosticConfig, CheckStatus, DiagnosticState
from noc.core.checkers.base import Check, CheckResult, DataItem
from noc.core.validators import is_oid


class ProfileDiagnostic:
    """
    Run diagnostic by config and check status
    """

    method_check_map = {
        "http_get": HTTP_DIAG,
        "https_get": HTTPS_DIAG,
    }

    def __init__(self, config: DiagnosticConfig, logger=None) -> None:
        self.config = config
        self.logger = logger or logging.getLogger("profilediagnostic")
        self.unsupported_method: set[str] = set()
        self.reason: str | None = None
        self.result_cache: dict[tuple[str, str], str] = {}
        self.profile: str | None = None
        self.ignoring_snmp = False
        self.oids = []
        self.urls = []
        self.rules: dict[tuple[str, str, int], list[SuggestProfile]] = self.load_rules()

    def iter_checks(
        self,
        address: str,
        labels: list[str] | None = None,
        groups: list[str] | None = None,
        cred: SNMPCredential | SNMPv3Credential | None = None,
        **kwargs,
    ) -> Iterable[tuple[Check, ...]]:
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

    def parse_checks(self, checks: list[CheckResult]):
        """Update checks data"""
        for c in checks:
            if c.check.startswith("SNMP"):
                method = "snmp_v2c_get"
            else:
                method = {HTTP_DIAG: "http_get", HTTPS_DIAG: "https_get"}[c.check]
            if not c.status:
                self.unsupported_method.add(method)
                continue
            for d in c.data or []:
                self.logger.info("[%s] Getting %s, Result: %s", method, d.name, d.value)
                self.result_cache[(method, d.name)] = d.value

    def process_result(
        self,
        checks: list[CheckResult],
        source: InputSource | None = InputSource.UNKNOWN,
    ) -> tuple[list[CheckStatus], list[DataItem]]:
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
            if method in self.unsupported_method or not r_key[1]:
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
                # {"profile": rule.profile}, []
                return [], [DataItem(name="profile", value=rule.profile)]
            error = f"Not find profile for OID or HTTP string: {result}"
        self.logger.info("Cannot detect profile: %s", error)
        self.reason = error
        # Data
        return [], []

    def get_check_status(
        self,
        checks: list[CheckStatus],
        **kwargs,
    ) -> tuple[DiagnosticState | None, str | None]:
        """"""
        if self.profile:
            return DiagnosticState.enabled, self.reason
        return DiagnosticState.failed, self.reason

    def load_rules(self) -> dict[tuple[str, str, int], list[SuggestProfile]]:
        """
        Convert list to tree: (method, param) -> Rules
        """
        r = defaultdict(list)
        for rule in ProfileCheckRule.get_profile_check_rules():
            r[rule.query_key].append(rule)
            if rule.method == "snmp_v2c_get":
                param = self.clean_snmp_param(rule.param)
                if param and param not in self.oids:
                    self.oids.append(param)
            elif rule.method in ("http_get", "https_get"):
                if (rule.method, rule.param) not in self.urls:
                    self.urls.append((rule.method, rule.param))
        return r

    def find_profile(self, key, result: str) -> SuggestProfile | None:
        if key not in self.rules:
            self.logger.warning("Not find rule for method: %s", key)
            return None
        for rule in self.rules[key]:
            if rule.is_match(result):
                return rule

    def clean_snmp_param(self, param):
        try:
            param = mib[param]
        except KeyError:
            self.logger.error("Cannot resolve OID '%s'. Ignoring", param)
            return None
        if not is_oid(param):
            self.logger.error("Bad OID format OID '%s'. Ignoring", param)
            return None
        return param

    def get_profile(self) -> tuple[str | None, str | None]:
        unsupported_method = set()
        snmp_result, http_result = "", ""
        for method, param, pref in sorted(self.rules, key=lambda x: x[2]):
            if method == "snmp_v2c_get":
                r_key = (method, self.clean_snmp_param(param))
            else:
                r_key = (method, param)
            if method in unsupported_method or not r_key[1]:
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
        else:
            error = None
        self.logger.info("Cannot detect profile: %s", error)
        return None, error
