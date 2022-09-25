# ---------------------------------------------------------------------
# Diagnostics check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Dict, List, Optional, Literal, Iterable, Any
from collections import defaultdict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.checkers.base import (
    Checker,
    Check,
    CheckResult,
    CheckData,
    ProfileSet,
    CredentialSet,
    MetricValue,
)
from noc.core.checkers.loader import loader
from noc.core.wf.diagnostic import DiagnosticState
from noc.sa.models.profile import Profile
from noc.pm.models.metrictype import MetricType


class DiagnosticCheck(DiscoveryCheck):
    """
    Diagnostic Check discovery
    """

    name = "diagnostic"
    CHECKERS: Dict[str, Checker] = {}  # Checkers Instance
    CHECK_MAP: Dict[str, str] = {}  # CheckName -> CheckerName mapping

    CHECK_CACHE = {}  # Cache check result

    def __init__(self, job, run_order: Optional[Literal["S", "E"]] = None):
        super().__init__(job)
        self.run_order = run_order

    def load_checkers(self):
        """
        Load available checkers
        :return:
        """
        for checker in loader:
            self.CHECKERS[checker] = loader[checker](self.object, self.logger, "discovery")
            for c in self.CHECKERS[checker].CHECKS:
                self.CHECK_MAP[c] = self.CHECKERS[checker].name

    def handler(self):
        # Loading checkers
        self.load_checkers()
        bulk = []
        metrics: List[MetricValue] = []
        # Diagnostic Data
        d_data: Dict[str, Any] = defaultdict(dict)  # Diagnostic -> Data
        last_state: Dict[str, DiagnosticState] = {}
        # Processed Check ? Filter param
        for dc in self.object.iter_diagnostic_configs():
            # Check on Discovery run
            if (self.is_box and not dc.discovery_box) or (
                self.is_periodic and not dc.discovery_periodic
            ):
                continue
            if dc.run_order != self.run_order:
                continue
            if not dc.checks or dc.blocked:
                # Diagnostic without checks
                continue
            if dc.run_policy not in {"A", "F"}:
                self.logger.info("[%s] Diagnostic for manual run. Skipping", dc.diagnostic)
                continue
            if (
                dc.run_policy == "F"
                and dc.diagnostic in self.object.diagnostics
                and self.object.get_diagnostic(dc.diagnostic).state == DiagnosticState.enabled
                and self.object.get_diagnostic(dc.diagnostic).checks
            ):
                self.logger.info("[%s] Diagnostic with enabled state. Skipping", dc.diagnostic)
                continue
            # Get checker
            checks: List[CheckResult] = []
            for cr in self.iter_checks(dc.checks):
                if cr.action and not hasattr(self, f"action_{cr.action.action}"):
                    self.logger.warning(
                        "[%s|%s] Unknown action: %s", dc.diagnostic, cr.check, cr.action.action
                    )
                elif cr.action:
                    h = getattr(self, f"action_{cr.action.action}")
                    h(cr.action)
                checks.append(cr)
                m_labels = [f"noc::check::name::{cr.check}", f"noc::diagnostic::{dc.diagnostic}"]
                if cr.arg0:
                    m_labels += [f"noc::check::arg0::{cr.arg0}"]
                metrics += [MetricValue("Check | Status", value=int(cr.status), labels=m_labels)]
                if cr.metrics:
                    metrics += cr.metrics
                if cr.data:
                    d_data[dc.diagnostic].update(cr.data)
            # Update diagnostics
            self.object.update_diagnostics(
                [
                    CheckData(
                        name=cr.check,
                        arg0=cr.arg0,
                        status=cr.status,
                        skipped=cr.skipped,
                        error=cr.error,
                        data=cr.data,
                    )
                    for cr in checks
                ],
                bulk=bulk,
            )
        if bulk:
            self.logger.info("Diagnostic changed: %s", ", ".join(di.diagnostic for di in bulk))
            self.object.save_diagnostics(self.object.id, bulk)
            self.object.sync_diagnostic_alarm([d.diagnostic for d in bulk])
            for di in bulk:
                self.object.register_diagnostic_change(
                    di.diagnostic,
                    state=di.state,
                    from_state=last_state.get(di.diagnostic, DiagnosticState.unknown),
                    data=d_data.get(di.diagnostic),
                    reason=di.reason,
                    ts=di.changed,
                )
        #
        if metrics:
            self.register_diagnostic_metrics(metrics)
        # Fire workflow event diagnostic ?

    def iter_checks(self, checks: List[Check]) -> Iterable[CheckResult]:
        r = []
        # Group check by checker
        do_checks: Dict[str, List[Check]] = defaultdict(list)
        for c in checks:
            if c.name not in self.CHECK_MAP:
                self.logger.warning("[%s] Unknown check. Skipping", c.name)
                continue
            if c in self.CHECK_CACHE:
                r.append(self.CHECK_CACHE[c])
                continue
            do_checks[self.CHECK_MAP[c.name]] += [c]
        for checker, d_checks in do_checks.items():
            checker = self.CHECKERS[checker]
            self.logger.info("[%s] Run checker", ";".join(f"{c.name}({c.arg0})" for c in d_checks))
            try:
                for check in checker.iter_result(d_checks):
                    yield check
            except Exception as e:
                self.logger.error("[%s] Error when run checker: %s", checker.name, str(e))

    def action_set_sa_profile(self, data: ProfileSet):
        """
        Setting Object Profile Check result
        :param data:
        :return:
        """
        # if "profile" not in data:
        #     return  # Cannot detect
        profile = Profile.get_by_name(data.profile)
        if profile.id == self.object.profile.id:
            self.logger.info("Profile is correct: %s", profile)
        else:
            self.logger.info(
                "Profile change detected: %s -> %s. Fixing database, resetting platform info",
                self.object.profile.name,
                profile.name,
            )
            self.invalidate_neighbor_cache()
            self.object.profile = profile
            self.object.vendor = None
            self.object.plarform = None
            self.object.version = None
            self.object.save()
            self.object.update_init()

    def action_set_credential(self, data: CredentialSet):
        """
        :param data:
        :return:
        """
        changed = False
        # For password change - cleanup credential ?
        for cred in ["snmp_ro", "snmp_rw", "user", "password", "super_password"]:
            nc = getattr(data, cred)
            if not nc:
                continue
            oc = getattr(self.object, cred, None)
            if nc != oc:
                changed = True
                setattr(self.object, cred, nc)
        # Reset auth profile to continue operations with new credentials
        if changed:
            self.logger.info("Setting credentials")
            self.object.auth_profile = None
            self.object.save()
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
