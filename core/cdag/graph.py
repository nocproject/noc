# ----------------------------------------------------------------------
# CDAG
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
from typing import Optional, Any, Dict, List

# NOC modules
from .node.base import BaseCDAGNode
from .node.loader import loader
from .tx import Transaction


class CDAG(object):
    def __init__(self, graph_id: str, state: Optional[Dict[str, Any]] = None):
        self.graph_id = graph_id
        self.state: Dict[str, Any] = state or {}
        self.nodes: Dict[str, BaseCDAGNode] = {}

    def __getitem__(self, item: str) -> BaseCDAGNode:
        return self.nodes[item]

    def __contains__(self, item: str):
        return item in self.nodes

    def add_node(
        self,
        node_id: str,
        node_type: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        sticky: bool = False,
    ) -> BaseCDAGNode:
        if node_id in self.nodes:
            raise ValueError("Node %s is already configured" % node_id)
        node_cls = loader.get_class(node_type)
        if not node_cls:
            raise ValueError("Invalid node type: %s" % node_type)
        config = config or {}
        #
        node = node_cls.construct(
            node_id,
            description=description,
            state=self.state.get(node_id),
            config=config,
            sticky=sticky,
        )
        self.nodes[node_id] = node
        return node

    def begin(self) -> Transaction:
        """
        Start new transaction
        :return:
        """
        return Transaction(self)

    def get_node(self, name: str) -> Optional[BaseCDAGNode]:
        return self.nodes.get(name)

    def get_state(self) -> Dict[str, Any]:
        """
        Construct current state
        :return:
        """
        r = {}
        for node_id, node in self.nodes.items():
            if not hasattr(node, "state_cls"):
                continue
            ns = node.get_state()
            if ns is None:
                continue
            r[node_id] = ns.model_dump()
        return r

    def merge(self, other: "CDAG", prefix: Optional[str] = "") -> "CDAG":
        """
        Merge other graph into this one
        :param other:
        :param prefix: Optional merged node's prefix
        :return:
        """
        # Merge nodes
        nodes: Dict[str, BaseCDAGNode] = {}
        for node_id, node in other.nodes.items():
            # Normalize name
            if node.sticky or not prefix:
                new_id = node_id
            else:
                new_id = f"{prefix}::{node_id}"
            if new_id in self.nodes:
                # Already installed
                nodes[node_id] = self.nodes[new_id]
            else:
                # Clone
                nodes[node_id] = node.clone(new_id)
        # Merge subscribers
        for node_id, o_node in other.nodes.items():
            node = nodes[node_id]
            for rs in o_node.iter_subscribers():
                node.subscribe(
                    nodes[rs.node.node_id], rs.input, dynamic=rs.node.is_dynamic_input(rs.input)
                )
        #
        return self

    def get_dot(self) -> str:
        """
        Build graphviz dot representation for graph

        :return:
        """
        n_map: Dict[str, str] = {}
        r = ["digraph {", '  rankdir="LR";']
        tb: List[str] = []
        tb_conn: List[str] = []
        tb_count = itertools.count()
        # Nodes
        for n, node_id in enumerate(sorted(self.nodes)):
            dot_id = f"n{n:05d}"
            n_map[node_id] = dot_id
            node = self.nodes[node_id]
            n_attrs = ""
            if node.config:
                attrs = []
                for fn in node.iter_config_fields():
                    v = getattr(node.config, fn)
                    if hasattr(v, "value"):
                        v = v.value
                    attrs += [f"{fn}: {v}"]
                if attrs:
                    n_attrs = "\\n" + "\\n".join(attrs)
            if node.sticky:
                style = ', style="bold"'
            else:
                style = ""
            r += [
                f'  {dot_id} [label="{node_id}\\ntype: {node.name}{n_attrs}", shape="{node.dot_shape}"{style}];'
            ]
            unbound = list(node.iter_unbound_inputs())
            if unbound:
                tbc = []
                for n in unbound:
                    cnt = next(tb_count)
                    tb_name = f"p{cnt:05d}"
                    tbc += [f"<{tb_name}> {n}"]
                    tb_conn += [f'  TB:{tb_name} -> {dot_id} [label="{n}"];']
                tb_labels = " | ".join(tbc)
                tb += [f"{{ {node_id} | {{ {tb_labels} }}}}"]
        # Render terminal block and its edges
        if tb:
            tb_label = " | ".join(tb)
            r.insert(2, f'  TB [label="{tb_label}" ,shape="record", style="bold"];')
            r += tb_conn
        # Edges
        for node in self.nodes.values():
            for rs in node.iter_subscribers():
                r += [f'  {n_map[node.node_id]} -> {n_map[rs.node.node_id]} [label="{rs.input}"];']
        r += ["}"]
        return "\n".join(r)
