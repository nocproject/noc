# ----------------------------------------------------------------------
# Interval discovery job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import random

# Third-party modules
import cachetools

# NOC modules
from ..base import MODiscoveryJob
from .metrics import MetricsCheck
from noc.core.span import Span
from noc.core.change.policy import change_tracker


class IntervalDiscoveryJob(MODiscoveryJob):
    name = "interval"

    _interval_cache = cachetools.TTLCache(maxsize=30000, ttl=3600)

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
        return self.object.object_profile.enable_metrics and super().can_run()

    def get_running_policy(self):
        return self.object.get_effective_periodic_discovery_running_policy()

    @cachetools.cachedmethod(operator.attrgetter("_interval_cache"), key=lambda s: s.object.id)
    def get_interval(self):
        if self.object:
            return self.object.get_metric_discovery_interval()
        # Dereference error
        return random.randint(60, 120)

    def get_failed_interval(self):
        return self.object.get_metric_discovery_interval()

    def can_update_alarms(self):
        return False
