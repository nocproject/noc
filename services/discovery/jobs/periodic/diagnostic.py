# ---------------------------------------------------------------------
# Diagnostics check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Dict, List, Optional, Literal, Iterable, Union, Tuple
from collections import defaultdict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.checkers.base import Check, CheckResult, MetricValue
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.checkers.loader import loader
from noc.core.wf.diagnostic import DiagnosticState, DiagnosticHub
from noc.core.debug import error_report
from noc.core.script.scheme import Protocol, SNMPCredential, CLICredential, SNMPv3Credential
from noc.sa.models.profile import Profile
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.sa.models.profilecheckrule import ProfileCheckRule
from noc.pm.models.metrictype import MetricType
from noc.config import config


class DiagnosticCheck(DiscoveryCheck):
    """
    Diagnostic Check discovery
    """

    name = "diagnostic"

    def __init__(self, job, run_order: Optional[Literal["S", "E"]] = None):
        super().__init__(job)
        self.run_order = run_order
        self.suggest_rules = CredentialCheckRule.get_suggests(self.object)

    def handler(self):
        # Loading checkers
        metrics: List[MetricValue] = []
        # Processed Check ? Filter param
        with DiagnosticHub(
            self.object,
            sync_alarm=self.job.can_update_alarms(),
            sync_labels=config.discovery.sync_diagnostic_labels,
            logger=self.logger,
        ) as d_hub:
            for di in d_hub:
                dc = di.config
                # Check on Discovery run
                if (self.is_box and not dc.discovery_box) or (
                    self.is_periodic and not dc.discovery_periodic
                ):
                    continue
                if dc.run_order != self.run_order:
                    continue
                if dc.blocked or not (dc.checks or dc.diagnostic_handler):
                    # Diagnostic without checks
                    continue
                if dc.run_policy not in {"A", "F"}:
                    self.logger.info("[%s] Diagnostic for manual run. Skipping", di.diagnostic)
                    continue
                if dc.run_policy == "F" and di.state == DiagnosticState.enabled and di.checks:
                    self.logger.info("[%s] Diagnostic with enabled state. Skipping", di.diagnostic)
                    continue
                # Get checker
                credentials: List[
                    Tuple[Protocol, Union[SNMPCredential, CLICredential, SNMPv3Credential]]
                ] = []
                for do_checks in d_hub.iter_active_checks(di.diagnostic):
                    checks: List[CheckResult] = []
                    for cr in self.run_checks(do_checks):
                        if cr.credential:
                            credentials += [(Protocol[cr.check], cr.credential)]
                        checks.append(cr)
                        m_labels = [
                            f"noc::check::name::{cr.check}",
                            f"noc::diagnostic::{di.diagnostic}",
                        ]
                        if cr.arg0:
                            m_labels += [f"noc::check::arg0::{cr.arg0}"]
                        if cr.address:
                            m_labels += [f"noc::check::address::{cr.address}"]
                        if not cr.skipped:
                            metrics += [
                                MetricValue("Check | Status", value=int(cr.status), labels=m_labels)
                            ]
                        if cr.metrics:
                            metrics += cr.metrics
                    # Update diagnostics
                    d_hub.update_checks(checks)
                # Apply Profile
                # if di.diagnostic == PROFILE_DIAG and "profile" in d_data[d.diagnostic]:
                #    self.set_profile(d_data[d.diagnostic]["profile"])
                # Apply credentials
                if credentials and (
                    not self.object.auth_profile or self.object.auth_profile.enable_suggest
                ):
                    self.logger.debug("Apply credentials: %s", credentials)
                    self.apply_credentials(credentials)
                # Update diagnostics
                # d_hub.update_checks(checks)
        # if metrics:
        #     self.register_diagnostic_metrics(metrics)
        # self.object.diagnostic.refresh_diagnostics()
        self.logger.debug("Object Diagnostics: %s", self.object.diagnostics)
        # Fire workflow event diagnostic ?

    def run_checks(self, checks: Tuple[Check, ...]) -> List[CheckResult]:
        self.logger.debug("Call checks on activator: %s", checks)
        script_checks, do_checks = [], []
        r = []
        for c in checks:
            if not c.script:
                do_checks.append(c)
            else:
                script_checks.append(c)
        if script_checks:
            try:
                r += self.object.scripts.run_checks(script_checks)
            except RPCError as e:
                self.logger.error("RPC Error: %s", e)
        if do_checks:
            try:
                r += open_sync_rpc(
                    "activator", pool=self.object.pool.name, calling_service="discovery"
                ).run_checks(checks)
            except RPCError as e:
                self.logger.error("RPC Error: %s", e)
        return [CheckResult.from_dict(c) for c in r]

    def iter_checks(self, checks: List[Check]) -> Iterable[CheckResult]:
        # Group check by checker
        do_checks: Dict[str, List[Check]] = defaultdict(list)
        for check in checks:
            checker = loader[check.name]
            if not checker:
                self.logger.warning("[%s] Unknown check. Skipping", check.name)
                continue
            if check.name == "PROFILE":
                cred = self.object.credentials.get_snmp_credential()
                if cred:
                    check = Check(check.name, credential=cred)
            do_checks[checker.name] += [check]
        for checker, d_checks in do_checks.items():
            params = self.get_checker_param(checker)
            checker = loader[checker](**params)
            self.logger.info("[%s] Run checker", ";".join(f"{c.name}({c.arg0})" for c in d_checks))
            try:
                for check in checker.iter_result(d_checks):
                    yield check
            except Exception as e:
                if self.logger.isEnabledFor(logging.DEBUG):
                    error_report()
                self.logger.error("[%s] Error when run checker: %s", checker.name, str(e))

    def get_checker_param(self, checker: str) -> Dict[str, str]:
        r = {
            "logger": self.logger,
            "calling_service": "discovery",
            "pool": self.object.pool.name,
            "object": self.object.id,
            "address": self.object.address,
        }
        if checker == "profile":
            r["rules"] = ProfileCheckRule.get_profile_check_rules()
        elif checker in ["snmp", "cli"] and (
            not self.object.auth_profile or self.object.auth_profile.enable_suggest
        ):
            r["rules"] = self.suggest_rules
        if checker == "cli":
            r["profile"] = self.object.profile
        return r

    def set_profile(self, profile: str) -> bool:
        profile = Profile.get_by_name(profile)
        if self.object.profile.id == profile.id:
            return False
        self.logger.info("Changed profile: %s -> %s", self.object.profile.name, profile.name)
        self.invalidate_neighbor_cache()
        self.object.profile = profile
        self.object.vendor = None
        self.object.platform = None
        self.object.version = None
        self.object.save()
        return True

    def apply_credentials(
        self,
        credentials: List[Tuple[Protocol, Union[CLICredential, SNMPCredential, SNMPv3Credential]]],
    ):
        changed = {}
        object_credentials = self.object.credentials
        for protocol, cred in credentials:
            if (
                isinstance(cred, (SNMPCredential, SNMPv3Credential))
                and object_credentials.snmp_security_level != cred.security_level
            ):
                self.object.snmp_security_level = cred.security_level
                changed["snmp_security_level"] = cred.security_level
            elif isinstance(cred, CLICredential) and self.object.scheme != protocol.value:
                changed["scheme"] = protocol.value
            for f in object_credentials.__dataclass_fields__:
                if not hasattr(cred, f) or getattr(cred, f) == getattr(object_credentials, f):
                    continue
                changed[f] = getattr(cred, f)
        if not changed:
            self.logger.info("Nothing credential changed")
            return
        if self.object.auth_profile:
            self.object.auth_profile = None
            changed["auth_profile"] = None
        for f, v in changed.items():
            self.logger.info("Update field: %s", f)
            setattr(self.object, f, v)
        ManagedObject.objects.filter(id=self.object.id).update(**changed)
        if "auth_profile" in changed:
            self.apply_credentials(credentials)
            return
        self.object._reset_caches(self.object.id, credential=True)
        self.object.update_init()

    def register_diagnostic_metrics(self, metrics: List[MetricValue]):
        """
        Metrics Labels:
          noc::diagnostic::<name>
          noc::check::<name>
          arg0
        :param metrics:
        :return:
        """
        r = {}
        now = datetime.datetime.now()
        # Group Metric by row
        for m in metrics:
            mt = MetricType.get_by_name(m.metric_type)
            if not mt:
                self.logger.warning("Unknown MetricType: %s", m.metric_type)
                continue
            if mt.scope.table_name not in r:
                r[mt.scope.table_name] = {}
            key = tuple(m.labels or [])
            if key not in r[mt.scope.table_name]:
                r[mt.scope.table_name][key] = {
                    "date": now.date().isoformat(),
                    "ts": now.replace(microsecond=0).isoformat(sep=" "),
                    "managed_object": self.object.bi_id,
                    "labels": m.labels,
                    mt.field_name: m.value,
                }
                continue
            r[mt.scope.table_name][key][mt.field_name] = m.value
        for table, data in r.items():
            self.service.register_metrics(table, list(data.values()), key=self.object.bi_id)
