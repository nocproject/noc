# ----------------------------------------------------------------------
# ConfigCDAGFactory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

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
    description: str | None = None
    config: dict[str, Any] | None = None
    inputs: list[InputItem] | None = None
    match: dict[str, Any] | None = None
    sticky: bool = False


class GraphConfig(BaseModel):
    nodes: list[NodeItem]


class ConfigCDAGFactory(BaseCDAGFactory):
    """
    Build CDAG from abstract config
    """

    def __init__(
        self,
        graph: CDAG,
        config: GraphConfig,
        ctx: FactoryCtx | None = None,
        namespace: str | None = None,
        nodes_config: dict[str, dict[str, Any]] | None = None,
        node_config_prefix: str | None = None,
    ):
        super().__init__(graph, ctx, namespace)
        self.config = config
        self.nodes_config = nodes_config or {}
        self.node_config_prefix = node_config_prefix

    def requirements_met(self, inputs: list[InputItem] | None):
        if not inputs:
            return True
        return all(self.expand_input(input.node) in self.graph for input in inputs)

    def is_matched(self, expr: FactoryCtx | None) -> bool:
        if not expr:
            return True
        return match(self.ctx, expr)

    def clean_node_config(self, node_id: str, config: dict[str, Any] | None) -> Any:
        return config

    def construct(self) -> None:
        # node_configs, node_states, inputs
        # Raise KeyError when not required inputs
        for item in self.config.nodes:
            # Check match
            if not self.is_matched(item.match):
                continue
            # Check for prerequisites
            if not self.requirements_met(item.inputs):
                continue
            # Override config
            override = None
            if self.nodes_config:
                config_id = (
                    f"{self.node_config_prefix}::{item.name}"
                    if self.node_config_prefix
                    else item.name
                )
                override = self.nodes_config.get(config_id)
            # Create node
            node_id = self.get_node_id(item.name)
            node = self.graph.add_node(
                node_id,
                node_type=item.type,
                description=item.description,
                config=self.clean_node_config(node_id, item.config),
                override_config=override,
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
