## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EffectiveSettings data structure
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

class EffectiveSettings(object):
    def __init__(self, metric=None, metric_type=None, is_active=True,
                 storage_rule=None, probe=None, interval=None,
                 thresholds=None):
        """
        "metric",  # Graphite metric name
        "metric_type",  # MetricType object
        "is_active",  # Activity mark
        "storage_rule",  # StorageRule object
        "probe",  # Probe object
        "interval",  # Polling interval, seconds
        "thresholds"  # [low_error, low_warn, high_warn, high_error
        """
        self.metric = metric
        self.metric_type = metric_type
        self.is_active = is_active
        self.storage_rule = storage_rule
        self.probe = probe
        self.interval = interval
        self.thresholds = thresholds

    def dump(self):
        r = []
        for n in ["metric", "metric_type", "is_active", "storage_rule",
                  "probe", "interval", "thresholds"]:
            r += ["%s='%s'" % (n, getattr(self, n))]
        return " ".join(r)
