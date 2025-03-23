# ---------------------------------------------------------------------
# Diagnostics check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import List, Optional, Literal, Union, Tuple

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.checkers.base import Check, CheckResult, MetricValue
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.wf.diagnostic import DiagnosticState, DiagnosticHub
from noc.core.script.scheme import SNMPCredential, CLICredential, SNMPv3Credential
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.pm.models.metrictype import MetricType
from noc.core.checkers.loader import loader
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
                if dc.blocked:
                    self.logger.info(
                        "[%s] Diagnostic blocked by settings: %s", di.diagnostic, di.reason
                    )
                    continue
                if not dc.checks and not dc.diagnostic_handler:
                    # Diagnostic without checks
                    self.logger.debug("[%s] Diagnostic without checks", di.diagnostic)
                    continue
                if dc.run_policy not in {"A", "F"}:
                    self.logger.info("[%s] Diagnostic for manual run. Skipping", di.diagnostic)
                    continue
                if dc.run_policy == "F" and di.state == DiagnosticState.enabled and di.checks:
                    self.logger.info("[%s] Diagnostic with enabled state. Skipping", di.diagnostic)
                    continue
                self.logger.info("[%s] Run diagnostic checks", di.diagnostic)
                # Get checker
                credential: Union[SNMPCredential, CLICredential, SNMPv3Credential] = None
                for do_checks in d_hub.iter_checks(di.diagnostic):
                    # Do nothing check ?
                    checks: List[CheckResult] = []
                    for cr in self.run_checks(do_checks):
                        if (
                            di.config.allow_set_credentials
                            and not cr.skipped
                            and cr.status
                            and cr.credential
                            and not credential
                        ):
                            credential = cr.credential
                        checks.append(cr)
                    # Update diagnostics
                    d_hub.update_checks(checks)
                    self.logger.debug("[%s] Collected check Result: %s", di.diagnostic, checks)
                # Apply credentials
                if credential and (
                    not self.object.auth_profile or self.object.auth_profile.enable_suggest
                ):
                    self.logger.debug("Apply credentials: %s", credential)
                    self.object.update_credentials(credential)
                # Update diagnostics
                # d_hub.update_checks(checks)
        # self.object.diagnostic.refresh_diagnostics()
        self.logger.debug("Object Diagnostics: %s", self.object.diagnostics)
        # Fire workflow event diagnostic ?

    def run_checks(self, checks: Tuple[Check, ...]) -> List[CheckResult]:
        self.logger.debug("Call checks on activator: %s", checks)
        script_checks, do_checks = [], []
        r = []
        for c in checks:
            if c.script or loader.is_script(c.name):
                script_checks.append(c)
            else:
                do_checks.append(c)
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
