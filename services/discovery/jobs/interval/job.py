# ----------------------------------------------------------------------
# Segment discovery job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random

# NOC modules
from ..base import MODiscoveryJob
from .metrics import MetricsCheck
from noc.sa.models.managedobject import ManagedObject
from noc.core.span import Span
from noc.core.change.policy import change_tracker


class IntervalDiscoveryJob(MODiscoveryJob):
    name = "interval"
    model = ManagedObject

    def handler(self, **kwargs):
        with Span(sample=self.object.periodic_telemetry_sample), change_tracker.bulk_changes():
            if self.allow_sessions():
                self.logger.debug("Using CLI sessions")
                with self.object.open_session():
                    self.run_checks()
            else:
                self.run_checks()

    def run_checks(self):
        if self.object.object_profile.enable_metrics:
            MetricsCheck(self).run()

    def can_run(self):
        return super().can_run() and self.object.object_profile.enable_metrics

    def get_running_policy(self):
        return self.object.get_effective_periodic_discovery_running_policy()

    def get_interval(self):
        if self.object:
            return self.object.get_metric_discovery_interval()
        else:
            # Dereference error
            return random.randint(60, 120)

    def get_failed_interval(self):
        return self.object.get_metric_discovery_interval()

    def can_update_alarms(self):
        return False
