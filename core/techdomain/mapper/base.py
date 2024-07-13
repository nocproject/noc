# ----------------------------------------------------------------------
# BaseMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import List, Iterable

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.inv.models.object import Object
from noc.core.resource import from_resource
from ..tracer.base import BaseTracer, Endpoint


@dataclass
class Node(object):
    object_id: str
    model: str
    endpoints: List[str]
    inputs: List[str]
    outputs: List[str]
    children: List["Node"]

    def to_dot(self) -> Iterable[str]:
        r = [f"subgraph cluster_{self.object_id} {{"]
        r.append(f'graph [label = "{self.model}"]')
        if self.endpoints:
            ep_label = "|".join(f"<{ep}>{ep}" for ep in self.endpoints)
            r.append(f'ep_{self.object_id} [shape = record label = "{ep_label}"]')
        if self.inputs:
            in_label = "|".join(f"<{i}>{i}" for i in self.inputs)
            r.append(f'in_{self.object_id} [shape = record label = "{in_label}"]')
        if self.outputs:
            out_label = "|".join(f"<{o}>{o}" for o in self.outputs)
            r.append(f'out_{self.object_id} [shape = record label = "{out_label}"]')
        if self.children:
            for c in self.children:
                r.extend(c.to_dot())
        r.append("}")
        return r

    def get_ref(self, name: str) -> str:
        if name in self.endpoints:
            return f"ep_{self.object_id}:{name}"
        if name in self.inputs:
            return f"in_{self.object_id}:{name}"
        if name in self.outputs:
            return f"out_{self.object_id}:{name}"
        msg = "Invalid ref"
        raise ValueError(msg)


class BaseMapper(object):
    name: str = "base"

    def __init__(self, channel: Channel):
        self.logger = PrefixLoggerAdapter(logging.getLogger("tracer"), self.name)
        self.nodes = {}
        self.channel = channel

    def get_node(self, obj: Object) -> None:
        node = self.nodes.get(str(obj.id))
        if node:
            return node
        node = Node(
            object_id=str(obj.id),
            model=obj.model.get_short_label(),
            endpoints=[],
            inputs=[],
            outputs=[],
            children=[],
        )
        self.nodes[node.object_id] = node
        return node

    def to_dot(self, channnel: Channel) -> str:
        raise NotImplementedError

    def get_tracer(self) -> BaseTracer:
        raise NotImplementedError

    def to_dot(self) -> str:
        tr = self.get_tracer()
        starting = []
        for ep in DBEndpoint.objects.filter(channel=self.channel.id):
            o, p = from_resource(ep.resource)
            if not p:
                continue
            node = self.get_node(o)
            node.endpoints.append(p)
            if ep.is_root:
                starting.append(Endpoint(object=o, name=p))
        # Trace path
        if self.channel.is_unidirectional:
            edge_style = " dir = forward"
        else:
            edge_style = ""
        edges = set()
        for ep in starting:
            last_pi = None
            for pi in tr.iter_path(ep):
                node = self.get_node(pi.object)
                if pi.input not in node.inputs and pi.input not in node.endpoints:
                    node.inputs.append(pi.input)
                if pi.output and pi.output not in node.outputs and pi.output not in node.endpoints:
                    node.outputs.append(pi.output)
                if last_pi:
                    # Edge from previous item
                    s_ref = self.nodes[str(last_pi.object.id)].get_ref(last_pi.output)
                    e_ref = self.nodes[str(pi.object.id)].get_ref(pi.input)
                    edges.add(f"{s_ref} -- {e_ref} [{edge_style}]")
                # Internal edge
                if pi.output:
                    n = self.nodes[str(pi.object.id)]
                    s_ref = n.get_ref(pi.input)
                    e_ref = n.get_ref(pi.output)
                    edges.add(f"{s_ref} -- {e_ref} [{edge_style} style = dashed]")
                last_pi = pi
        r = ["graph {", "graph [rankdir = LR]"]
        for n in self.nodes.values():
            r.extend(n.to_dot())
        r.extend(edges)
        r.append("}")
        return "\n".join(r)
