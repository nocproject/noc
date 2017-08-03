# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Periodic Discovery Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import random
# NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob
from uptime import UptimeCheck
from interfacestatus import InterfaceStatusCheck
from mac import MACCheck
from metrics import MetricsCheck


class PeriodicDiscoveryJob(MODiscoveryJob):
    name = "periodic"
    umbrella_cls = "Discovery | Job | Periodic"

    # Store context
    context_version = 1

    def handler(self, **kwargs):
        if self.object.auth_profile and self.object.auth_profile.type == "S":
            self.logger.info("Invalid credentials. Stopping")
            return
        self.reboot_detected = False
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
        if self.object.object_profile.enable_periodic_discovery_mac:
            MACCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_metrics:
            MetricsCheck(self).run()

    def init_context(self):
        if "counters" not in self.context:
            self.context["counters"] = {}
        if "metric_windows" not in self.context:
            self.context["metric_windows"] = {}

    def can_run(self):
        return (
            self.object.is_managed and
            self.object.object_profile.enable_periodic_discovery and
            self.object.object_profile.periodic_discovery_interval
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
