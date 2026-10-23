# ----------------------------------------------------------------------
# ValueNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class ValueNodeConfig(BaseModel):
    value: ValueType


class ValueNode(BaseCDAGNode):
    """
    Always activate with given value
    """

    name = "value"
    config_cls = ValueNodeConfig
    dot_shape = "cds"
    categories = [Category.UTIL]

    def get_value(self) -> ValueType | None:
        return self.config.value
