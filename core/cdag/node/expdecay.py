# ----------------------------------------------------------------------
# ExpDecayNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List
from math import exp

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .window import WindowNode, WindowConfig

from .base import ValueType, Category

NS = 1_000_000_000


class ExpDecayNodeState(BaseModel):
    times: List[int] = []
    values: List[ValueType] = []


class ExpDecayNodeConfig(WindowConfig):
    k: float = 1.0


class ExpDecayNode(WindowNode):
    """
    Calculate exponential decay function over window. k - decay factor
    """

    name = "expdecay"
    config_cls = ExpDecayNodeConfig
    categories = [Category.WINDOW]

    def get_window_value(
        self, values: List[ValueType], timestamps: List[int]
    ) -> Optional[ValueType]:
        t0 = timestamps[-1] // NS
        nk = self.config.k
        return sum(v * exp(nk * t0 - ts // NS) for ts, v in zip(timestamps, values))
