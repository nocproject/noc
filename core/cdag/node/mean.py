# ----------------------------------------------------------------------
# MeanNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel
import numpy as np

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class MeanNodeState(BaseModel):
    values: List[float] = []


class MeanNodeConfig(BaseModel):
    min_window: int = 3
    max_window: int = 100


class MeanNode(BaseCDAGNode):
    """
    Calculate estimated mean value
    """

    name = "mean"
    config_cls = MeanNodeConfig
    state_cls = MeanNodeState
    categories = [Category.STATISTICS]

    def get_stats(self, values: np.array) -> float:
        return np.mean(values)

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        self.state.values.insert(0, float(x))
        # Trim
        if len(self.state.values) >= self.config.max_window:
            self.state.values = self.state.values[: self.config.max_window]
        # Check window is filled
        if len(self.state.values) < self.config.min_window:
            return None
        values = np.array(self.state.values)
        return self.get_stats(values)
