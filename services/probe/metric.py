# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging

MAX31 = 0x7FFFFFFFL
MAX32 = 0xFFFFFFFFL
MAX64 = 0xFFFFFFFFFFFFFFFFL


class Metric(object):
    # Threshold states
    ST_NORMAL = 0
    ST_LOW_WARN = -1
    ST_LOW_ERROR = -2
    ST_HIGH_WARN = 1
    ST_HIGH_ERROR = 2

    STATES = {
        ST_NORMAL: "NORMAL",
        ST_LOW_WARN: "LOW_WARNING",
        ST_LOW_ERROR: "LOW_ERROR",
        ST_HIGH_WARN: "HIGH_WARNING",
        ST_HIGH_ERROR: "HIGH_ERROR"
    }

    def __init__(self, task):
        self.task = task
        self.managed_object= None
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
        self.max_counter = None
        self.locked_convert = False  # Convert changed by set_convert
        self.state = self.ST_NORMAL

    def configure(self, metric, metric_type, thresholds, convert,
                  scale=1.0, managed_object=None, **kwargs):
        if metric_type != self.metric_type:
            self.reset()
            self.metric_type = metric_type
        self.managed_object = managed_object
        self.metric = metric
        self.thresholds = thresholds
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
            self.task.service.spool_metric(self.metric, int(t), r)
            self.check_thresholds(t, r)

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
                self.task.logger.info(
                    "[%s] Possible counter stepback: %s -> %s",
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

    def check_thresholds(self, t, v):
        """
        Check value against defined thresholds
        """
        if self.thresholds[0] is not None and v <= self.thresholds[0]:
            self.set_state(t, v, self.ST_LOW_ERROR)
        elif self.thresholds[1] is not None and v <= self.thresholds[1]:
            self.set_state(t, v, self.ST_LOW_WARN)
        elif self.thresholds[3] is not None and v >= self.thresholds[3]:
            self.set_state(t, v, self.ST_HIGH_ERROR)
        elif self.thresholds[2] is not None and v >= self.thresholds[2]:
            self.set_state(t, v, self.ST_HIGH_WARN)
        else:
            self.set_state(t, v, self.ST_NORMAL)

    def set_state(self, t, v, state):
        if state != self.state:
            old_state = self.STATES[self.state]
            new_state = self.STATES[state]
            self.task.logger.info(
                "[%s] state transition: %s -> %s",
                self.metric, old_state, new_state
            )
            # Send event
            self.task.service.spool_event(
                self.managed_object,
                t,
                {
                    "metric": self.metric,
                    "metric_type": self.metric_type,
                    "ts": t,
                    "value": v,
                    "old_state": old_state,
                    "new_state": new_state
                }
            )
            self.state = state
