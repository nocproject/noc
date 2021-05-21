# ----------------------------------------------------------------------
# ValueNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any

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

    def __init__(
        self,
        node_id: str,
        state: Optional[Dict[str, Any]] = None,
        description: str = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(node_id, state=state, description=description, config=config)

    def get_value(self) -> Optional[ValueType]:
        return self.config.value
