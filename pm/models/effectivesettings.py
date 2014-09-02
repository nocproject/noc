## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EffectiveSettings data structure
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import uuid
from collections import namedtuple

EffectiveSettingsMetric = namedtuple("EffectiveSettingsMetric", [
    "metric", "metric_type", "thresholds", "convert", "scale"
])

class EffectiveSettings(object):
    def __init__(self, metric=None, metric_type=None, is_active=True,
                 storage_rule=None, probe=None, interval=None,
                 thresholds=None, handler=None, config=None,
                 errors=None, model_id=None, object=None, convert=None,
                 scale=1.0, metrics=None):
        """
        :param metric: Graphite metric name
        :param metric_type: MetricType object
        :param is_active: Activity mark
        :param storage_rule: StorageRule object
        :param probe: Probe object
        :param interval: Polling interval, seconds
        :param thresholds: [low_error, low_warn, high_warn, high_error
        :param handler: Name of probe's handler to use
        :param config: dict of config
        :param errors: list of errors
        """
        self.metric = metric
        self.metric_type = metric_type
        self.is_active = is_active
        self.storage_rule = storage_rule
        self.probe = probe
        self.interval = interval
        self.thresholds = thresholds
        self.handler = handler
        self.config = config
        self.errors = errors or []
        self.traces = []
        self.model_id = model_id
        self.object = object
        self.convert = convert
        self.scale = scale
        self.metrics = metrics

    def dump(self):
        r = []
        for n in ["model_id", "object",
                  "is_active", "storage_rule",
                  "probe", "interval", "handler"]:
            r += ["%20s : %s" % (n, getattr(self, n))]
        if self.metrics:
            r += ["%20s :" % "metrics"]
            for m in self.metrics:
                for n in ["metric", "metric_type", "convert", "scale",
                          "thresholds"]:
                    r += ["%30s : %s" % (n, getattr(m, n))]
        if self.config:
            r += ["%20s :" % "config"]
            for k in self.config:
                r += ["%30s : %s" % (k, self.config[k])]
        if self.traces:
            r += ["%20s :" % "traces"]
            for t in self.traces:
                r += ["%20s   %s" % ("", t)]
        if self.errors:
            r += ["%20s :" % "errors"]
            for t in self.errors:
                r += ["%20s   %s" % ("", t)]
        return "\n".join(r)

    def error(self, msg):
        self.errors += [msg]

    def trace(self, msg):
        self.traces += [msg]

    @property
    def uuid(self):
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                "%s-%s-%s-%s-%s" % (
                    str(self.model_id), str(self.object.id),
                    str(self.probe.id), str(self.handler),
                    self.interval)
            )
        )
