# ----------------------------------------------------------------------
# BaseCDAGFactory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from ..typing import FactoryCtx
from ..graph import CDAG


class BaseCDAGFactory(object):
    """
    CDAG factory is responsible for computation graph construction. Factories can be chained
    together
    """

    def __init__(
        self, graph: CDAG, ctx: Optional[FactoryCtx] = None, namespace: Optional[str] = None
    ):
        self.graph = graph
        self.ctx = ctx
        self.namespace = namespace

    def construct(self) -> None:  # pragma: no cover
        raise NotImplementedError

    def get_node_id(self, name: str) -> str:
        """
        Generate prefixed node id
        :param name:
        :return:
        """
        if self.namespace and "::" not in name:
            return f"{self.namespace}::{name}"
        return name
