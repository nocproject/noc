# ----------------------------------------------------------------------
# IndicartorNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class IndicatorConfig(BaseModel):
    true_level: ValueType = 1
    false_level: ValueType = 0


class IndicatorNode(BaseCDAGNode):
    """
    Activates `true_level` if value of `x` is greater or equal to zero.
    Activates `false_level` otherwise.
    """

    name = "indicator"
    config_cls = IndicatorConfig
    categories = [Category.ACTIVATION]

    def get_value(self, x: ValueType) -> Optional[ValueType]:
        return self.config.true_level if x >= 0 else self.config.false_level
