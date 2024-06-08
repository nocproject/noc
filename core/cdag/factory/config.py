# ----------------------------------------------------------------------
# ConfigCDAGFactory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Any

# Third-party modules
from pydantic import BaseModel
from jinja2 import Template

# NOC modules
from noc.core.matcher import match
from .base import BaseCDAGFactory, FactoryCtx
from ..graph import CDAG


class InputItem(BaseModel):
    name: str
    node: str
    dynamic: bool = False


class NodeItem(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    inputs: Optional[List[InputItem]] = None
    match: Optional[Dict[str, Any]] = None
    sticky: bool = False


class GraphConfig(BaseModel):
    nodes: List[NodeItem]


class ConfigCDAGFactory(BaseCDAGFactory):
    """
    Build CDAG from abstract config
    """

    def __init__(
        self,
        graph: CDAG,
        config: GraphConfig,
        ctx: Optional[FactoryCtx] = None,
        namespace: Optional[str] = None,
    ):
        super().__init__(graph, ctx, namespace)
        self.config = config

    def requirements_met(self, inputs: Optional[List[InputItem]]):
        if not inputs:
            return True
        for input in inputs:
            if self.expand_input(input.node) not in self.graph:
                return False
        return True

    def is_matched(self, expr: Optional[FactoryCtx]) -> bool:
        if not expr:
            return True
        return match(self.ctx, expr)

    def clean_node_config(self, node_id: str, config: Optional[Dict[str, Any]]) -> Any:
        return config

    def construct(self) -> None:
        for item in self.config.nodes:
            # Check match
            if not self.is_matched(item.match):
                continue
            # Check for prerequisites
            if not self.requirements_met(item.inputs):
                continue
            # Create node
            node_id = self.get_node_id(item.name)
            node = self.graph.add_node(
                node_id,
                node_type=item.type,
                description=item.description,
                config=self.clean_node_config(node_id, item.config),
                sticky=item.sticky,
            )
            # Connect node
            if item.inputs:
                for input in item.inputs:
                    r_node = self.graph[self.expand_input(input.node)]
                    r_node.subscribe(node, input.name, dynamic=input.dynamic)

    def expand_input(self, name: str) -> str:
        if "{" in name:
            name = Template(name).render(**self.ctx)
        return self.get_node_id(name)
