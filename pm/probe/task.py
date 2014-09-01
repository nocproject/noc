# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Probe task
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
import time
import logging
## NOC modules
from noc.pm.probes.base import probe_registry
from noc.lib.debug import error_report
from metric import Metric


class Task(object):
    def __init__(self, daemon):
        self.daemon = daemon
        self.uuid = None
        self.handler = None
        self.handler_name = None
        self.interval = None
        self.config = None
        self.offset = None
        self.running = False
        self.next_run = None
        self.last_run = None
        self.probe = None
        self.metrics = []
        self.mdata = {}  # metric type -> Metric
        self.default_metric_type = None

    def __repr__(self):
        return u"<Task %s>" % self.uuid

    def __cmp__(self, other):
        return cmp(self.next_run, other.next_run)

    def debug(self, msg):
        logging.debug("[%s] %s" % (self.uuid, msg))

    def run(self):
        self.running = True
        try:
            self.debug("Running")
            result = self.handler(self.probe, **self.config)
            self.debug("Result %s" % result)
            if result is not None:
                t = time.time()
                if not isinstance(result, dict):
                    if self.default_metric_type:
                        result = {self.default_metric_type: result}
                    else:
                        raise ValueError("Handler must return dict")
                # Feed result
                for m in result:
                    if m in self.mdata:
                        self.mdata[m].set_value(t, result[m])
            self.debug("Done")
        except:
            error_report()
        self.last_run = self.next_run
        self.next_run = self.get_next_run()
        self.running = False
        self.daemon.reschedule(self)

    def configure(self, uuid, handler, interval, metrics,
                  config, **kwargs):
        self.uuid = uuid
        self.handler_name = handler
        nh = probe_registry.get_handler(handler)
        if nh != self.handler:
            self.handler = nh
            self.probe = nh.im_class(self.daemon)
        if interval != self.interval:
            # Change offset
            self.offset = interval * random.random()
            self.interval = interval
            self.next_run = self.get_next_run()
            if not self.running:
                self.daemon.reschedule(self)
        self.config = config
        # Apply metrics
        if self.metrics != metrics:
            self.metrics = metrics
            c = set(self.mdata)
            n = set(m["metric_type"] for m in metrics)
            # Remove metrics
            for m in c - n:
                del self.mdata[m]
            # Create metrics
            for m in n - c:
                self.mdata[m] = Metric(self.daemon)
            # Configure metrics
            for m in metrics:
                self.mdata[m["metric_type"]].configure(**m)
            if len(metrics) == 1:
                self.default_metric_type = metrics[0]["metric_type"]
            else:
                self.default_metric_type = None

    def get_next_run(self):
        now = time.time()
        nt = (now // self.interval) * self.interval + self.offset
        if nt < now:
            nt += self.interval
        return nt
