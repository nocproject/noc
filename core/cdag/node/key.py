# ----------------------------------------------------------------------
# KeyNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseCDAGNode, ValueType, Category


class KeyNode(BaseCDAGNode):
    """
    Pass `in` to output only when `key` is activated with non-zero
    """

    name = "key"
    categories = [Category.UTIL]

    def get_value(self, key: ValueType, x: ValueType) -> Optional[ValueType]:
        if not key:
            return None
        return x
