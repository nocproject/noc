# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


MAX32 = 0xFFFFFFFFL
MAX64 = 0xFFFFFFFFFFFFFFFFL


class Metric(object):
    def __init__(self, daemon):
        self.daemon = daemon
        self.metric_type = None
        self.metric = None
        self.thresholds = None
        self.convert = None
        self.last_value = None
        self.last_time = None
        self.convert = None
        self.collector = None
        self.cvt = None

    def configure(self, metric, metric_type, thresholds, convert,
                  collector, **kwargs):
        if metric_type != self.metric_type:
            self.reset()
            self.metric_type = metric_type
        self.metric = metric
        self.thresholds = thresholds
        self.collector = collector
        if convert != self.convert:
            self.reset()
            self.convert = convert
            self.cvt = getattr(self, "convert_%s" % convert)

    def set_value(self, t, v):
        r = self.cvt(t, v)
        self.last_time = t
        self.last_value = v
        if r is not None:
            self.daemon.sender.feed(self.collector, self.metric, int(t), r)
            # @todo: Check thresholds

    def reset(self):
        self.last_value = None
        self.last_time = None

    def convert_none(self, t, v):
        return v

    def convert_counter(self, t, v):
        if not self.last_time or not self.last_value:
            return None
        if v < self.last_value:
            # Counter wrap
            mc = MAX64 if self.last_value >= MAX32 else MAX32
            self.last_value -= mc
        return (v - self.last_value) / (t - self.last_time)
