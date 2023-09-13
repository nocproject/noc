# ----------------------------------------------------------------------
# subgraph node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Optional, List, Iterable, Dict, DefaultDict
from collections import defaultdict
from dataclasses import dataclass

# Third-party modules
from pydantic import BaseModel
import yaml

# NOC modules
from ..graph import CDAG
from ..factory.config import ConfigCDAGFactory, GraphConfig
from .base import BaseCDAGNode, ValueType, Category, IN_INVALID, IN_REQUIRED


class InputMapping(BaseModel):
    # Outer input name
    public_name: str
    # Local node
    node: str
    # Local node input name
    name: str


class ConfigMapping(BaseModel):
    # Outer config param name
    name: str
    # Local node
    node: str
    # Local node param name
    param: str


class SubgraphConfig(BaseModel):
    # Yaml-serialized subgraph
    cdag: str
    inputs: Optional[List[InputMapping]]
    output: Optional[str]
    config: Optional[List[ConfigMapping]]


class SubgraphState(BaseModel):
    state: Optional[Dict[str, Any]] = None


class SubgraphCDAGFactory(ConfigCDAGFactory):
    def __init__(self, *args, **kwargs):
        # node -> [(param, value)]
        self.node_cfg: DefaultDict[str, Dict[str, Any]] = defaultdict(dict)
        super().__init__(*args, **kwargs)

    def set_node_config(self, node: str, param: str, value: Any) -> None:
        """
        Set additional node config
        :param node:
        :param param:
        :param value:
        :return:
        """
        self.node_cfg[node][param] = value

    def clean_node_config(self, node_id: str, config: Optional[Dict[str, Any]]) -> Any:
        override = self.node_cfg[node_id]
        if override:
            config = config or {}
            config.update(**override)
        return config


@dataclass
class InputItem(object):
    __slots__ = "node", "input"
    node: BaseCDAGNode
    input: str


class SubgraphNode(BaseCDAGNode):
    """
    Execute nested subgraph
    """

    name = "subgraph"
    config_cls = SubgraphConfig
    state_cls = SubgraphState
    categories = [Category.UTIL]
    __slots__ = "state", "cdag", "input_mappings", "measure_node"

    def __init__(
        self,
        node_id: str,
        prefix: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        description: str = None,
        config: Optional[Dict[str, Any]] = None,
        sticky: bool = False,
    ):
        # Clean up config
        cfg: SubgraphConfig = self.clean_config(config)
        # Get graph config
        graph_cfg = GraphConfig(**yaml.safe_load(cfg.cdag))
        # Build graph
        self.state = self.clean_state(state)
        self.cdag = CDAG("inner", state=self.state.state)
        factory = SubgraphCDAGFactory(self.cdag, config=graph_cfg)
        if cfg.config:
            for m in cfg.config:
                factory.set_node_config(m.node, m.param, config.get(m.name))
        factory.construct()
        # Build input mappings
        self.input_mappings: Dict[str, InputItem] = {}
        if cfg.inputs:
            for m in cfg.inputs:
                node = self.cdag.get_node(m.node)
                if not node:
                    continue
                self.input_mappings[m.public_name] = InputItem(node=node, input=m.name)
        # Inject measure node when necessary
        self.measure_node = None
        if cfg.output:
            self.measure_node = self.cdag.add_node(f"__measure_{id(self)}", "none")
            self.cdag.get_node(cfg.output).subscribe(self.measure_node, "x")
        # Construct all the rest
        super().__init__(
            node_id=node_id,
            prefix=prefix,
            state=state,
            description=description,
            config=config,
            sticky=sticky,
        )

    def iter_inputs(self) -> Iterable[str]:
        yield from self.input_mappings

    def get_input_type(self, name: str) -> int:
        if name in self.input_mappings:
            return IN_REQUIRED
        return IN_INVALID

    def get_value(self, *args, **kwargs) -> Optional[ValueType]:
        # Start sub-transaction
        tx = self.cdag.begin()
        for p, v in kwargs.items():
            im = self.input_mappings[p]
            im.node.activate(tx, im.input, v)
        changed_state = tx.get_changed_state()
        if changed_state:
            if self.state.state:
                self.state.state.update(changed_state)
            else:
                self.state.state = changed_state.copy()
        out = tx.get_inputs(self.measure_node)
        return out.get("x")  # None node has `x` input
