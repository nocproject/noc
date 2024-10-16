# ---------------------------------------------------------------------
# Diagnostics check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Dict, List, Optional, Literal, Iterable, Any
from collections import defaultdict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.checkers.base import (
    ObjectChecker,
    Check,
    CheckResult,
    CheckData,
    CapsItem,
    CredentialItem,
    MetricValue,
)
from noc.core.checkers.loader import loader
from noc.core.wf.diagnostic import DiagnosticState, DiagnosticHub
from noc.core.debug import error_report
from noc.sa.models.profile import Profile
from noc.sa.models.managedobject import ManagedObject
from noc.pm.models.metrictype import MetricType
from noc.config import config


class DiagnosticCheck(DiscoveryCheck):
    """
    Diagnostic Check discovery
    """

    name = "diagnostic"
    CHECKERS: Dict[str, ObjectChecker] = {}  # Checkers Instance
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
            self.CHECKERS[checker] = loader[checker]
            for c in self.CHECKERS[checker].CHECKS:
                self.CHECK_MAP[c] = self.CHECKERS[checker].name

    def handler(self):
        # Loading checkers
        self.load_checkers()
        metrics: List[MetricValue] = []
        # Diagnostic Data
        d_data: Dict[str, Any] = defaultdict(dict)  # Diagnostic -> Data
        # Processed Check ? Filter param
        with DiagnosticHub(
            self.object,
            sync_alarm=self.job.can_update_alarms(),
            sync_labels=config.discovery.sync_diagnostic_labels,
            logger=self.logger,
        ) as d_hub:
            for d in d_hub:
                dc = d.config
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
                    self.logger.info("[%s] Diagnostic for manual run. Skipping", d.diagnostic)
                    continue
                if dc.run_policy == "F" and d.state == DiagnosticState.enabled and d.checks:
                    self.logger.info("[%s] Diagnostic with enabled state. Skipping", d.diagnostic)
                    continue
                # Get checker
                checks: List[CheckResult] = []
                credentials: List[CredentialItem] = []
                capabilities: List[CapsItem] = []
                for cr in self.iter_checks(dc.checks):
                    if cr.credentials:
                        credentials += cr.credentials
                    if cr.caps:
                        capabilities += cr.caps
                    checks.append(cr)
                    m_labels = [f"noc::check::name::{cr.check}", f"noc::diagnostic::{d.diagnostic}"]
                    if cr.arg0:
                        m_labels += [f"noc::check::arg0::{cr.arg0}"]
                    if not cr.skipped:
                        metrics += [
                            MetricValue("Check | Status", value=int(cr.status), labels=m_labels)
                        ]
                    if cr.metrics:
                        metrics += cr.metrics
                    if cr.data:
                        d_data[d.diagnostic].update(cr.data)
                # Apply credentials
                if credentials and (
                    not self.object.auth_profile or self.object.auth_profile.enable_suggest
                ):
                    self.logger.debug("Apply credentials: %s", credentials)
                    self.apply_credentials(credentials)
                # Update diagnostics
                d_hub.update_checks(
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
                )
        if metrics:
            self.register_diagnostic_metrics(metrics)
        # self.object.diagnostic.refresh_diagnostics()
        self.logger.debug("Object Diagnostics: %s", self.object.diagnostics)
        # Fire workflow event diagnostic ?

    def iter_checks(self, checks: List[Check]) -> Iterable[CheckResult]:
        # r = []
        # Group check by checker
        do_checks: Dict[str, List[Check]] = defaultdict(list)
        for c in checks:
            if c.name not in self.CHECK_MAP:
                self.logger.warning("[%s] Unknown check. Skipping", c.name)
                continue
            if self.CHECK_MAP[c.name] not in self.CHECKERS:
                self.logger.warning("[%s] Unknown checker. Skipping", c.name)
                continue
            do_checks[self.CHECK_MAP[c.name]] += [c]
        for checker, d_checks in do_checks.items():
            checker = self.CHECKERS[checker](self.object, self.logger, "discovery")
            self.logger.info("[%s] Run checker", ";".join(f"{c.name}({c.arg0})" for c in d_checks))
            try:
                for check in checker.iter_result(d_checks):
                    yield check
            except Exception as e:
                if self.logger.isEnabledFor(logging.DEBUG):
                    error_report()
                self.logger.error("[%s] Error when run checker: %s", checker.name, str(e))

    def apply_credentials(self, credentials: List[CredentialItem]):
        """
        Set credentials to ManagedObject
        :param credentials:
        :return:
        """
        changed = {}
        object_credentials = self.object.credentials
        for cred in credentials:
            if not hasattr(self.object, cred.field):
                # Unknown attribute
                continue
            if (
                hasattr(object_credentials, cred.field)
                and getattr(object_credentials, cred.field) == cred.value
            ):
                # Same credential
                continue
            # Profile processed
            if cred.field == "profile":
                profile = (
                    Profile.get_default_profile()
                    if cred.op == "reset"
                    else Profile.get_by_name(cred.value)
                )
                if profile.id == self.object.profile.id:
                    self.logger.info("Profile is correct: %s", profile)
                    continue
                changed.update(
                    {"vendor": None, "platform": None, "version": None, "profile": str(profile.id)}
                )
            elif cred.field == "scheme":
                if self.object.scheme == int(cred.value):
                    continue
                changed[cred.field] = int(cred.value) if cred.op == "set" else 1
            elif getattr(self.object, cred.field) != cred.value:
                changed[cred.field] = cred.value if cred.op == "set" else None
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
        if "profile" in changed:
            # Invalidate Neighbor cache, Move to on_save ?
            self.invalidate_neighbor_cache()
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
