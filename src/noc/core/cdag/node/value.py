# ----------------------------------------------------------------------
# ValueNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

from .base import BaseCDAGNode, Category, ValueType


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
