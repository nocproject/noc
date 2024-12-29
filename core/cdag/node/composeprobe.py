# ----------------------------------------------------------------------
# ComposeProbeNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, Callable, FrozenSet
from time import time_ns

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .probe import ProbeNode, ValueType, Category
from .base import IN_REQUIRED
from noc.core.expr import get_fn


class ComposeProbeNodeConfig(BaseModel):
    unit: str
    expression: str
    is_delta: bool = False
    scale: str = "1"
    compose_inputs: FrozenSet[str] = None


logger = logging.getLogger(__name__)


class ComposeProbeNode(ProbeNode):
    """
    Entrance for calculate composed metrics. Accepts timestamp
    Converts counter when necessary
    """

    name = "composeprobe"
    config_cls = ComposeProbeNodeConfig
    categories = [Category.UTIL]

    __slots__ = ("expression",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expression: Callable = get_fn(self.config.expression)

    def get_value(self, **kwargs) -> Optional[ValueType]:
        try:
            x = self.expression(**kwargs)
        except Exception as e:
            logger.warning("[%s] Error when calculate value: %s", self.node_id, str(e))
            x = 0
        return super().get_value(x, ts=time_ns(), unit="1")

    @property
    def is_const(self) -> bool:
        return False

    def get_input_type(self, name: str) -> int:
        if name in self.config.compose_inputs:
            return IN_REQUIRED
        return super().get_input_type(name)

    @property
    def req_config_inputs_count(self) -> int:
        return len(self.config.compose_inputs)
