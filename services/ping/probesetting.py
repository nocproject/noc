# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Probe Setting
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import cachetools

tp_cache = {}

POLICY_MAP = {
    "f": 0,
    "a": 1
}


class ProbeSetting(object):
    __slots__ = [
        "id",
        "address",
        "name",
        "interval",
        "status",
        "policy",
        "size",
        "count",
        "timeout",
        "sent_status",
        "report_rtt",
        "report_attempts",
        "time_expr",
        "time_cond",
        "bi_id",
        "task"
    ]

    def __init__(self, id, address, name, interval, status=None,
                 policy="f", size=64, count=3, timeout=1000,
                 report_rtt=False, report_attempts=False,
                 time_expr=None, bi_id=None, *args, **kwargs):
        self.id = id
        self.address = address
        self.name = name
        self.interval = interval
        self.status = status
        self.policy = POLICY_MAP.get(policy, 0)
        self.size = max(size, 64)
        self.count = max(count, 1)
        self.timeout = max(timeout, 1)
        self.sent_status = None
        self.report_rtt = report_rtt
        self.report_attempts = report_attempts
        self.time_expr = time_expr
        self.time_cond = self.compile(time_expr)
        self.task = None
        self.bi_id = bi_id

    def update(self, interval, report_rtt, report_attempts=False,
               policy="f", size=64, count=3, timeout=1000,
               time_expr=None,
               *args, **kwargs):
        self.interval = interval
        self.policy = POLICY_MAP.get(policy, 0)
        self.size = max(size, 64)
        self.count = max(count, 1)
        self.timeout = max(timeout, 1)
        self.report_rtt = report_rtt
        self.report_attempts = report_attempts
        self.time_expr = time_expr
        self.time_cond = self.compile(time_expr)

    def is_differ(self, data):
        return (
            self.interval != data["interval"] or
            self.policy != POLICY_MAP.get(data.get("policy", "f"), 0) or
            self.size != max(data.get("size", 64), 64) or
            self.count != max(data.get("count", 3), 1) or
            self.timeout != max(data.get("timeout", 1000), 1) or
            self.report_rtt != data.get("report_rtt", False) or
            self.report_attempts != data.get("report_attempts", False) or
            self.time_expr != data.get("time_expr")
        )

    @classmethod
    @cachetools.cachedmethod(lambda _: tp_cache)
    def compile(cls, src):
        if src:
            try:
                return compile(src, "<string>", "eval")
            except SyntaxError:
                return None
        else:
            return None
