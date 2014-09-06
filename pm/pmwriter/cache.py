## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## metrics cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
from threading import Condition
import inspect
from noc.pm.pmwriter.strategies.base import DrainStrategy
import logging

logger = logging.getLogger(__name__)


class MetricsCache(object):
    def __init__(self, strategy="next"):
        self.cache = defaultdict(list)  # metric -> [(value, timestamp)]
        self.can_drain = Condition()
        self.locked_metrics = set()
        self.metric_released = Condition()
        self.strategy = None
        self.set_strategy(strategy)

    def set_strategy(self, strategy):
        m = __import__("noc.pm.pmwriter.strategies.%s" % strategy,
            {}, {}, "*")
        for n in dir(m):
            o = getattr(m, n)
            if (inspect.isclass(o) and issubclass(o, DrainStrategy)
                and o.name == strategy):
                self.strategy = o(self.cache)
                break
        if not self.strategy:
            logger.error("Invalid drain strategy: %s", strategy)
            raise ValueError("Invalid drain strategy: %s" % strategy)

    def register_metric(self, metric, value, timestamp):
        """
        Place metric to cache
        """
        self.cache[metric] += [(timestamp, value)]
        with self.can_drain:
            self.can_drain.notify()

    def iter_metrics(self):
        """
        Generator yielding metrics from cache
        """
        while True:
            # Get next metric according to strategy
            with self.can_drain:
                while not self.cache:
                    self.can_drain.wait()
                metric = self.strategy.get_item()
                data = self.cache.pop(metric)
            # Wait for locked metric
            with self.metric_released:
                while metric in self.locked_metrics:
                    self.metric_released.wait()
                self.locked_metrics.add(metric)
            yield metric, data

    def release_metric(self, metric):
        with self.metric_released:
            self.locked_metrics.remove(metric)
            self.metric_released.notify()
