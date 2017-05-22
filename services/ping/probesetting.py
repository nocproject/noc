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


class ProbeSetting(object):
    __slots__ = [
        "id",
        "address",
        "name",
        "interval",
        "status",
        "sent_status",
        "report_rtt",
        "report_attempts",
        "time_expr",
        "time_cond",
        "task"
    ]

    def __init__(self, id, address, name, interval, status=None,
                 report_rtt=False, report_attempts=False,
                 time_expr=None, *args, **kwargs):
        self.id = id
        self.address = address
        self.name = name
        self.interval = interval
        self.status = status
        self.sent_status = None
        self.report_rtt = report_rtt
        self.report_attempts = report_attempts
        self.time_expr = time_expr
        self.time_cond = self.compile(time_expr)
        self.task = None

    def update(self, interval, report_rtt, report_attempts=False,
               time_expr=None,
               *args, **kwargs):
        self.interval = interval
        self.report_rtt = report_rtt
        self.report_attempts = report_attempts
        self.time_expr = time_expr
        self.time_cond = self.compile(time_expr)

    def is_differ(self, data):
        return (
            self.interval != data["interval"] or
            self.report_rtt != data.get("report_rtt") or
            self.report_attempts != data.get("report_attempts") or
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
