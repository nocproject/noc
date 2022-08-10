# ----------------------------------------------------------------------
# MetricsNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Callable
import time

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.service.loader import get_service
from noc.core.perf import metrics
from .base import BaseCDAGNode, ValueType, Category


class MetricsNodeConfig(BaseModel):
    scope: str
    spool: bool = True


NS = 1_000_000_000

# scope -> name -> cleaner
scope_cleaners: Dict[str, Dict[str, Callable]] = {}


class MetricsNode(BaseCDAGNode):
    """
    Collect all dynamic inputs and send all of them as a metric JSON
    """

    name = "metrics"
    categories = [Category.UTIL]
    config_cls = MetricsNodeConfig
    dot_shape = "folder"

    def get_value(self, ts: int, labels: List[str], **kwargs) -> Optional[ValueType]:
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
        if self.config.spool:
            get_service().register_metrics(self.config.scope, [r])
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
