# ---------------------------------------------------------------------
# Periodic Discovery Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import random

# NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob
from noc.core.span import Span
from noc.core.change.policy import change_tracker
from ..box.resolver import ResolverCheck
from .uptime import UptimeCheck
from .interfacestatus import InterfaceStatusCheck
from .mac import MACCheck
from .alarms import AlarmsCheck
from .metrics import MetricsCheck
from .cpestatus import CPEStatusCheck
from .diagnostic import DiagnosticCheck


class PeriodicDiscoveryJob(MODiscoveryJob):
    name = "periodic"
    umbrella_cls = "Discovery | Job | Periodic"

    # Store context
    context_version = 1

    is_periodic = True
    default_contexts = ("counters", "metric_windows", "active_thresholds")

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

    def run_checks(self):
        if self.object.object_profile.enable_periodic_discovery_uptime:
            UptimeCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_interface_status:
            InterfaceStatusCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_cpestatus:
            CPEStatusCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_alarms:
            AlarmsCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_mac:
            MACCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_metrics:
            MetricsCheck(self).run()
        DiagnosticCheck(self, run_order="E").run()

    def get_running_policy(self):
        return self.object.get_effective_periodic_discovery_running_policy()

    def can_run(self):
        return (
            super().can_run()
            and self.object.object_profile.enable_periodic_discovery
            and self.object.object_profile.periodic_discovery_interval
        )

    def get_interval(self):
        if self.object:
            return self.object.object_profile.periodic_discovery_interval
        else:
            # Dereference error
            return random.randint(60, 120)

    def get_failed_interval(self):
        return self.object.object_profile.periodic_discovery_interval

    def can_update_alarms(self):
        return self.object.can_create_periodic_alarms()

    def get_fatal_alarm_weight(self):
        return self.object.object_profile.periodic_discovery_fatal_alarm_weight

    def get_alarm_weight(self):
        return self.object.object_profile.periodic_discovery_alarm_weight
