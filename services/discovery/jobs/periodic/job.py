# ---------------------------------------------------------------------
# Periodic Discovery Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import random
from typing import Optional

# NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob
from noc.core.span import Span
from noc.core.change.policy import change_tracker
from ..box.resolver import ResolverCheck
from .uptime import UptimeCheck
from .interfacestatus import InterfaceStatusCheck
from .mac import MACCheck
from .alarms import AlarmsCheck
from .cpestatus import CPEStatusCheck
from .diagnostic import DiagnosticCheck
from .metrics import MetricsCheck
from noc.config import config


class PeriodicDiscoveryJob(MODiscoveryJob):
    name = "periodic"
    umbrella_cls = "Discovery | Job | Periodic"

    # Store context
    context_version = 2

    is_periodic = True

    def handler(self, **kwargs):
        with Span(sample=self.object.periodic_telemetry_sample), change_tracker.bulk_changes():
            if self.object.auth_profile and self.object.auth_profile.type == "S":
                self.logger.info("Invalid credentials. Stopping")
                return
            ResolverCheck(self).run()
            DiagnosticCheck(self, run_order="S").run()
            if self.allow_sessions():
                self.logger.debug("Using CLI sessions")
                with self.object.open_session():
                    self.run_checks()
            else:
                self.run_checks()

    def is_run_interval(self, interval: int, run: int, name: Optional[str] = None) -> bool:
        """

        Attrs:
            interval: Job interval
            run: Number of job runs
            name: Discovery name
        """
        d_interval = self.get_interval()
        if run and interval != d_interval:
            p_sc = interval / d_interval
            if run % p_sc:  # runs
                self.logger.info(
                    "[%s] Skip due to schedule, next run in %s sec",
                    name or self.name,
                    interval - (run % p_sc) * d_interval,
                )
                return False
        return True

    def run_checks(self):
        runs = self.get_runs()
        if self.object.object_profile.enable_periodic_discovery_uptime and self.is_run_interval(
            self.get_discovery_interval("uptime"),
            runs,
            name="uptime",
        ):
            UptimeCheck(self).run()
        if (
            self.object.object_profile.enable_periodic_discovery_interface_status
            and self.is_run_interval(
                self.get_discovery_interval("interface_status"),
                runs,
                name="interface_status",
            )
        ):
            InterfaceStatusCheck(self).run()
        if self.object.object_profile.enable_metrics:
            MetricsCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_cpestatus and self.is_run_interval(
            self.get_discovery_interval("cpestatus"),
            runs,
            name="cpestatus",
        ):
            CPEStatusCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_alarms and self.is_run_interval(
            self.get_discovery_interval("alarms"),
            runs,
            name="alarms",
        ):
            AlarmsCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_mac and self.is_run_interval(
            self.get_discovery_interval("mac"),
            runs,
            name="mac",
        ):
            MACCheck(self).run()
        DiagnosticCheck(self, run_order="E").run()

    def get_running_policy(self):
        return self.object.get_effective_periodic_discovery_running_policy()

    def can_run(self):
        return super().can_run() and (
            (
                self.object.object_profile.enable_periodic_discovery
                and self.object.object_profile.periodic_discovery_interval
            )
            or self.object.object_profile.enable_metrics
        )

    def get_discovery_interval(self, name) -> int:
        """
        Getting discovery interval by check name
        :param name:
        :return:
        """
        if not getattr(self.object.object_profile, f"enable_periodic_discovery_{name}"):
            return 0
        return (
            getattr(self.object.object_profile, f"periodic_discovery_{name}_interval")
            or self.object.object_profile.periodic_discovery_interval
        )

    def get_interval(self) -> int:
        """Calculate discovery interval"""
        if not self.object:
            # Dereference error
            return random.randint(60, 120)
        intervals = [self.object.object_profile.periodic_discovery_interval]
        for check in ["uptime", "interface_status", "cpestatus", "alarms", "mac"]:
            interval = self.get_discovery_interval(check)
            if interval:
                intervals.append(interval)
        if self.object.object_profile.enable_metrics:
            intervals.append(
                max(
                    self.object.effective_metric_discovery_interval,
                    config.discovery.min_metric_interval,
                )
            )
        return min(intervals)

    def get_failed_interval(self):
        return self.object.object_profile.periodic_discovery_interval

    def can_update_alarms(self):
        return self.object.can_create_periodic_alarms()

    def get_fatal_alarm_weight(self):
        return self.object.object_profile.periodic_discovery_fatal_alarm_weight

    def get_alarm_weight(self):
        return self.object.object_profile.periodic_discovery_alarm_weight
