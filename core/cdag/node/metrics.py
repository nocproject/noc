# ----------------------------------------------------------------------
# MetricsNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
from typing import Optional, List, Dict, Callable, Any

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.service.loader import get_service
from noc.core.perf import metrics
from noc.core.mx import MX_METRICS_SCOPE, MX_LABELS, MessageType
from .base import BaseCDAGNode, ValueType, Category
from noc.config import config


class MetricsNodeConfig(BaseModel):
    scope: str
    spool: bool = True
    spool_message: bool = False
    message_meta: Optional[Dict[str, Any]] = None
    message_labels: Optional[bytes] = None


NS = 1_000_000_000

# scope -> name -> cleaner
scope_cleaners: Dict[str, Dict[str, Callable]] = {}
#
mx_converters: Optional[Dict[str, Callable]] = None


class MetricsNode(BaseCDAGNode):
    """
    Collect all dynamic inputs and send all of them as a metric JSON
    """

    name = "metrics"
    categories = [Category.UTIL]
    config_cls = MetricsNodeConfig
    dot_shape = "folder"
    mx_scopes = set(config.message.enable_metric_scopes)

    def get_value(self, ts: int, labels: List[str], **kwargs) -> Optional[Dict[str, ValueType]]:
        r = {}
        rk = {}
        cleaners = scope_cleaners.get(self.config.scope) or {}
        for k, v in kwargs.items():
            if v is None:
                continue
            if self.is_key_input(k):
                rk[k] = v
                continue
            cleaner = cleaners.get(k)
            if cleaner:
                try:
                    v = cleaner(v)
                except ValueError:
                    continue
            r[k] = v
        if not r:
            return None
        r.update(rk)
        t = time.gmtime(ts / NS)
        r["date"] = time.strftime("%Y-%m-%d", t)
        r["ts"] = time.strftime("%Y-%m-%d %H:%M:%S", t)
        if labels:
            r["labels"] = labels
        metrics["spooled_metrics", ("scope", self.config.scope)] += 1
        svc = get_service()
        if self.config.spool:
            svc.register_metrics(self.config.scope, [r])
        if self.config.spool_message and self.config.scope in self.mx_scopes:
            self.send_mx(r)
        return r

    @staticmethod
    def set_scope_cleaners(scope: str, cleaners: Dict[str, Callable]) -> None:
        """
        Set cleaners for scope
        :param scope: Scope name
        :param cleaners: Scope cleaners
        """
        if scope not in scope_cleaners:
            scope_cleaners[scope] = cleaners

    def send_mx(self, data):
        """
        Send collected metrics to MX Router
        :param data:
        :return:
        """
        global mx_converters

        if mx_converters is None:
            mx_converters = self.load_mx_converters()
        if self.config.scope not in mx_converters:
            return
        r = mx_converters[self.config.scope](data)
        if not r:
            return
        elif self.config.message_meta:
            r["meta"] = self.config.message_meta
        svc = get_service()
        svc.register_message(
            r,
            MessageType.METRICS,
            {
                MX_METRICS_SCOPE: self.config.scope.encode(encoding="utf-8"),
                MX_LABELS: self.config.message_labels or b"",
            },
            r["bi_id"],
            group_key=f'{self.config.scope}-{r["bi_id"]}',
        )

    @classmethod
    def load_mx_converters(cls):
        """
        Loading MX Metrics map rules
        :return:
        """
        from noc.main.models.metricstream import MetricStream

        r = {}
        for mss in MetricStream.objects.filter():
            if mss.is_active and mss.scope.table_name in set(config.message.enable_metric_scopes):
                r[mss.scope.table_name] = mss.to_mx
        return r
