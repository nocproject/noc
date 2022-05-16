# ----------------------------------------------------------------------
# Probe Setting
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from enum import Enum

# Third-party modules
import cachetools

# NOC modules
from noc.config import config

tp_cache = {}


class Policy(Enum):
    CHECK_FIRST = 0
    CHECK_ALL = 1


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
        "expr_policy",
        "bi_id",
        "task",
        "fm_pool",
        "stream",
        "partition",
    ]

    def __init__(
        self,
        id,
        address,
        name,
        interval,
        status=None,
        policy="f",
        size=64,
        count=3,
        timeout=1_000,
        report_rtt=False,
        report_attempts=False,
        time_expr=None,
        expr_policy="D",
        bi_id=None,
        fm_pool=None,
        *args,
        **kwargs,
    ):
        self.id = id
        self.address = address
        self.name = name
        self.interval = interval
        self.status = status
        self.policy = self._clean_policy(policy)
        self.size = max(size, 64)
        self.count = max(count, 1)
        self.timeout = self._clean_timeout(timeout)
        self.sent_status = None
        self.report_rtt = report_rtt
        self.report_attempts = report_attempts
        self.time_expr = time_expr
        self.time_cond = self.compile(time_expr)
        self.expr_policy = expr_policy
        self.task = None
        self.bi_id = bi_id
        self.fm_pool = fm_pool or config.pool
        self.stream = None
        self.partition = 0  # Set by set_partition
        self.set_stream()

    @staticmethod
    def get_pool_stream(pool: str) -> str:
        return "events.%s" % pool

    @staticmethod
    def _clean_timeout(timeout: int) -> float:
        return float(max(timeout, 1_000)) / 1_000.0

    @staticmethod
    def _clean_policy(policy: str) -> Policy:
        if policy == "a":
            return Policy.CHECK_ALL
        return Policy.CHECK_FIRST

    def set_stream(self):
        self.stream = self.get_pool_stream(self.fm_pool)

    def set_partition(self, num_partitions: int) -> None:
        self.partition = int(self.id) % num_partitions

    def update(
        self,
        interval,
        report_rtt,
        report_attempts=False,
        policy="f",
        size=64,
        count=3,
        timeout=1000,
        time_expr=None,
        expr_policy="D",
        fm_pool=None,
        *args,
        **kwargs,
    ):
        self.interval = interval
        self.policy = self._clean_policy(policy)
        self.size = max(size, 64)
        self.count = max(count, 1)
        self.timeout = self._clean_timeout(timeout)
        self.report_rtt = report_rtt
        self.report_attempts = report_attempts
        self.time_expr = time_expr
        self.time_cond = self.compile(time_expr)
        self.expr_policy = expr_policy
        self.fm_pool = fm_pool or config.pool
        self.set_stream()

    def is_differ(self, data):
        return (
            self.interval != data["interval"]
            or self.policy != self._clean_policy(data.get("policy", "f"))
            or self.size != max(data.get("size", 64), 64)
            or self.count != max(data.get("count", 3), 1)
            or self.timeout != max(data.get("timeout", 1000), 1)
            or self.report_rtt != data.get("report_rtt", False)
            or self.report_attempts != data.get("report_attempts", False)
            or self.time_expr != data.get("time_expr")
            or self.fm_pool != data.get("fm_pool")
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
