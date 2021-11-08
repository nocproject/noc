# ----------------------------------------------------------------------
# MetricsNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Callable
import time

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.service.loader import get_service
from .base import BaseCDAGNode, ValueType, Category


class MetricsNodeConfig(BaseModel):
    scope: str
    spool: bool = True


NS = 1_000_000_000


class MetricsNode(BaseCDAGNode):
    """
    Collect all dynamic inputs and send all of them as a metric JSON
    """

    name = "metrics"
    categories = [Category.UTIL]
    config_cls = MetricsNodeConfig
    dot_shape = "folder"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleaners: Dict[str, Callable] = {}

    def get_value(self, ts: int, labels: List[str], **kwargs) -> Optional[ValueType]:
        r = {}
        rk = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            if self.is_key_input(k):
                rk[k] = v
                continue
            cleaner = self.cleaners.get(k)
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
        if self.config.spool:
            get_service().register_metrics(self.config.scope, [r])
        return r

    def set_cleaner(self, name: str, cleaner: Callable) -> None:
        """
        Set ClickHouse field type for a given input
        :param name:
        :param cleaner: Callable to clean value or return None
        :return:
        """
        self.cleaners[name] = cleaner

    def clone(self, graph, node_id: str) -> Optional[BaseCDAGNode]:
        node = super().clone(graph, node_id)
        if not node:
            return None
        for k, v in self.cleaners.items():
            node.set_cleaner(k, v)
        for i in self.iter_key_inputs():
            node.mark_as_key(i)
        return node
