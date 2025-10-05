# ----------------------------------------------------------------------
# BaseCollector implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import time
from typing import Any, Tuple, Iterable

# Third-party modules
from django.db import connection

# NOC modules
from noc.core.perf import metrics
from noc.config import config
from noc.core.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)

Metric = Tuple[Tuple[Any], int]


class BaseCollector(object):
    name = None

    def __init__(self, service):
        self.service = service
        self.ttl = getattr(config.selfmon, "%s_ttl" % self.name, 30)
        self.last_metrics = {}
        self.logger = PrefixLoggerAdapter(logger, self.name)
        self.t0 = int(time.time())
        self.next_run = self.t0

    @classmethod
    def is_enabled(cls):
        return getattr(config.selfmon, "enable_%s" % cls.name)

    def can_run_at(self, t):
        """
        Check if collector can be run at time t
        :param t: timestamp
        :return:
        """
        return self.next_run <= t

    def schedule_next(self):
        self.next_run = self.t0 + ((int(time.time()) - self.t0) // self.ttl + 1) * self.ttl

    def run(self):
        self.logger.info("Running")
        left_metrics = set(self.last_metrics)
        # Collect metrics
        n = 0
        for metric, value in self.iter_metrics():
            self.last_metrics[metric] = value
            if metric in left_metrics:
                left_metrics.remove(metric)
            metrics[metric] = value
            n += 1
        # Delete left metrics
        for m in left_metrics:
            if m in metrics:
                del metrics[m]
        self.logger.info("Done. %d metrics collected", n)

    def iter_metrics(self) -> Iterable[Metric]:
        raise NotImplementedError()

    def pg_execute(self, sql, args=None):
        """
        Execute PostgreSQL query
        :param sql: SQL statement
        :param args: Additional args
        :return:
        """
        cursor = connection.cursor()
        cursor.execute(sql, args)
        return cursor.fetchall()

    @staticmethod
    def metric(metric: str, *, value: int, **kwargs: Any) -> Tuple[Tuple[Any], int]:
        return ((metric, *tuple((k, v) for k, v in kwargs.items() if v is not None)), value)
