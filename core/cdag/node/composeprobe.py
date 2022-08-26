# ----------------------------------------------------------------------
# ComposeProbeNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Callable
import inspect
import time

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .probe import ProbeNode, ValueType, Category
from noc.core.expr import get_fn


class ComposeProbeNodeConfig(BaseModel):
    unit: str
    expression: str
    scale: str = "1"


class ComposeProbeNode(ProbeNode):
    """
    Entrance for calculate composed metrics. Accepts timestamp
    Converts counter when necessary
    """

    name = "composeprobe"
    config_cls = ComposeProbeNodeConfig
    categories = [Category.UTIL]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expression: Callable = get_fn(self.config.expression)
        self.probe_inputs = set(inspect.signature(self.expression).parameters)

    def get_value(self, ts: int, **kwargs) -> Optional[ValueType]:
        x = self.expression(**kwargs)
        ts = ts or int(time.time())
        return super().get_value(x, ts=ts, unit="1")

    def is_required_input(self, name: str) -> bool:
        return name in self.probe_inputs
