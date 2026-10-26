# ----------------------------------------------------------------------
# KeyNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

from .base import BaseCDAGNode, Category, ValueType


class KeyNode(BaseCDAGNode):
    """
    Pass `in` to output only when `key` is activated with non-zero
    """

    name = "key"
    categories = [Category.UTIL]

    def get_value(self, key: ValueType, x: ValueType) -> ValueType | None:
        if not key:
            return None
        return x
