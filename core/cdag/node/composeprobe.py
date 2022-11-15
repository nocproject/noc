# ----------------------------------------------------------------------
# ComposeProbeNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect
from typing import Optional, Callable
from time import time_ns

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .probe import ProbeNode, ValueType, Category
from noc.core.expr import get_fn


class ComposeProbeNodeConfig(BaseModel):
    unit: str
    expression: str
    is_delta: bool = False
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
        self.static_inputs |= set(inspect.signature(self.expression).parameters)
        self.req_inputs_count = len(self.static_inputs)

    def get_value(self, **kwargs) -> Optional[ValueType]:
        x = self.expression(**kwargs)
        return super().get_value(x, ts=time_ns(), unit="1")
