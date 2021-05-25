# ----------------------------------------------------------------------
# CDAG
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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
        ctx: Optional[Dict[str, Any]] = None,
    ) -> BaseCDAGNode:
        if node_id in self.nodes:
            raise ValueError("Node %s is already configured" % node_id)
        node_cls = loader.get_class(node_type)
        if not node_cls:
            raise ValueError("Invalid node type: %s" % node_type)
        config = config or {}
        #
        return node_cls.construct(
            self,
            node_id,
            description=description,
            state=self.state.get(node_id),
            config=config,
            ctx=ctx,
        )

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
            r[node_id] = ns.dict()
        return r

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
                for fn in node.config.__fields__:
                    v = getattr(node.config, fn)
                    if hasattr(v, "value"):
                        v = v.value
                    attrs += [f"{fn}: {v}"]
                if attrs:
                    n_attrs = "\\n" + "\\n".join(attrs)
            r += [
                f'  {dot_id} [label="{node_id}\\ntype: {node.name}{n_attrs}", shape="{node.dot_shape}"];'
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
            r.insert(2, f'  TB [label="{tb_label}" ,shape="record"];')
            r += tb_conn
        # Edges
        for node in self.nodes.values():
            for r_node, in_name in node.iter_subscribers():
                r += [f'  {n_map[node.node_id]} -> {n_map[r_node.node_id]} [label="{in_name}"];']
        r += ["}"]
        return "\n".join(r)
