# ----------------------------------------------------------------------
# GaussNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
import numpy as np

# NOC modules
from .base import ValueType, Category
from .window import WindowNode, WindowConfig


class GaussNodeConfig(WindowConfig):
    n_sigma: float = 3.0
    true_level: ValueType = 1
    false_level: ValueType = 0
    skip_outliers: bool = True


class GaussNode(WindowNode):
    """
    Gaussian filter. Considering input values has normal distribution.
    Collect data and activate with `true_level` if |value - mean| < n_sigma * std
    """

    name = "gauss"
    config_cls = GaussNodeConfig
    categories = [Category.ML]

    def get_missed_value(self) -> Optional[ValueType]:
        return self.config.true_level

    def get_window_value(
        self, values: List[ValueType], timestamps: List[int]
    ) -> Optional[ValueType]:
        if len(values) == 1:
            return self.config.true_level  # pragma: no cover
        v = np.array(self.state.values[:-1])
        mean = np.mean(v)
        std = np.std(v)
        if abs(values[-1] - mean) <= self.config.n_sigma * std:
            return self.config.true_level
        if self.config.skip_outliers:
            del self.state.values[-1]
            del self.state.timestamps[-1]
        return self.config.false_level
