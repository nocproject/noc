# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Probe task
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## Third-party modules
import tornado.gen
## NOC modules
from noc.pm.probes.base import probe_registry
from noc.lib.debug import error_report
from metric import Metric
from noc.lib.log import PrefixLoggerAdapter
from noc.core.ioloop.timers import PeriodicOffsetCallback


class Task(PeriodicOffsetCallback):
    def __init__(self, service, interval):
        self.service = service
        self.logger = None
        self.uuid = None
        self.handler = None
        self.handler_name = None
        self.interval = None
        self.config = None
        self.probe = None
        self.metrics = []
        self.mdata = {}  # metric type -> Metric
        self.default_metric_type = None
        super(Task, self).__init__(self.run, interval)

    def __repr__(self):
        return u"<Task %s>" % self.uuid

    @tornado.gen.coroutine
    def run(self):
        try:
            self.logger.debug("Running")
            t0 = self.service.ioloop.time()
            result = yield self.handler(self.probe, **self.config)
            dt = (self.service.ioloop.time() - t0) * 1000.0
            self.logger.debug("Result %s (%.2fms)", result, dt)
            if result is not None:
                t = time.time()
                if not isinstance(result, dict):
                    if self.default_metric_type:
                        result = {self.default_metric_type: result}
                    else:
                        self.logger.error(
                            "Handler must return dict. Returned: %s",
                            result
                        )
                        raise ValueError("Handler must return dict")
                # Feed result
                for m in result:
                    if m in self.mdata:
                        v = result[m]
                        if v is not None:
                            self.mdata[m].set_value(t, v)
        except:
            error_report()

    def configure(self, uuid, handler, interval, metrics,
                  config, managed_object, **kwargs):
        if not self.uuid:
            self.logger = PrefixLoggerAdapter(self.service.logger, uuid)
        self.uuid = uuid
        self.handler_name = handler
        nh = probe_registry.get_handler(handler)
        if nh != self.handler:
            self.handler = nh
            self.probe = nh.im_class(self.service, self)
        if interval != self.interval:
            self.interval = interval
            self.set_callback_time(interval * 1000)
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
                self.mdata[m] = Metric(self)
            # Configure metrics
            for m in metrics:
                m["managed_object"] = managed_object
                self.mdata[m["metric_type"]].configure(**m)
            if len(metrics) == 1:
                self.default_metric_type = metrics[0]["metric_type"]
            else:
                self.default_metric_type = None

    def set_metric_convert(self, metric, convert=None, scale=None):
        self.mdata[metric].set_convert(convert, scale)
