# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from policy import FeedPolicy

MAX31 = 0xFFFFFFFFL
MAX32 = 0xFFFFFFFFL
MAX64 = 0xFFFFFFFFFFFFFFFFL

logger = logging.getLogger(__name__)


class Metric(object):
    def __init__(self, daemon):
        self.daemon = daemon
        self.metric_type = None
        self.metric = None
        self.thresholds = None
        self.convert = None
        self.last_value = None
        self.last_time = None
        self.last_result = None
        self.convert = None
        self.scale = None
        self.cvt = None
        self.policy = FeedPolicy()
        self.max_counter = None
        self.locked_convert = False  # Convert changed by set_convert

    def configure(self, metric, metric_type, thresholds, convert,
                  collectors, scale=1.0, **kwargs):
        if metric_type != self.metric_type:
            self.reset()
            self.metric_type = metric_type
        self.metric = metric
        self.thresholds = thresholds
        self.policy.configure(collectors)
        if not self.locked_convert:
            self.scale = scale
            if convert != self.convert:
                self.reset()
                self.convert = convert
                self.cvt = getattr(self, "convert_%s" % convert)

    def set_value(self, t, v):
        r = self.cvt(t, v)
        self.last_time = t
        self.last_value = v
        self.last_result = r
        if r is not None:
            r *= self.scale
            self.daemon.sender.feed(self.policy, self.metric, int(t), r)
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
            # Counter decreased, either wrap or stepback
            if self.max_counter is None:
                if self.last_value <= MAX31:
                    self.max_counter = MAX31
                elif self.last_value <= MAX32:
                    self.max_counter = MAX32
                else:
                    self.max_counter = MAX64
            # Direct distance
            d_direct = self.last_value - v
            # Counter wrap distance
            d_wrap = v + (self.max_counter - self.last_value)
            if d_direct < d_wrap:
                # Possible counter stepback
                logger.info(
                    "Possible counter stepback for %s: %s -> %s",
                    self.metric, self.last_value, v
                )
                # Repeat last result, even if None
                return self.last_result
            else:
                # Counter wrap
                return d_wrap / (t - self.last_time)
        else:
            # Normal counter increment
            return (v - self.last_value) / (t - self.last_time)

    def convert_derive(self, t, v):
        if not self.last_time or not self.last_value:
            return None
        return (v - self.last_value) / (t - self.last_time)

    def set_convert(self, convert=None, scale=None):
        self.locked_convert = True
        self.scale = scale if scale is not None else self.scale
        convert = convert if convert is not None else self.convert
        if convert != self.convert:
            self.reset()
            self.convert = convert
            self.cvt = getattr(self, "convert_%s" % convert)
