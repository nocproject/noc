# ----------------------------------------------------------------------
# PercentileNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# NOC modules
from .base import ValueType, Category
from .window import WindowNode, WindowConfig


class PercentileNodeConfig(WindowConfig):
    percentile: int


class PercentileNode(WindowNode):
    """
    Calculate percentile (in percents). Do not activate values until `min_window` is filled
    """

    name = "percentile"
    config_cls = PercentileNodeConfig
    categories = [Category.WINDOW]

    def get_window_value(
        self, values: List[ValueType], timestamps: List[int]
    ) -> Optional[ValueType]:
        wl = sorted(values)
        i = len(wl) * self.config.percentile // 100
        return wl[i]
