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
from noc.core.resource import from_resource
from ..tracer.base import BaseTracer, Endpoint, PathItem


@dataclass
class Node(object):
    label: str
    endpoints: List[str]
    inputs: List[str]
    outputs: List[str]

    @property
    def node_id(self) -> str:
        return str(id(self))

    def to_dot(self) -> Iterable[str]:
        r = [f"subgraph cluster_{self.node_id} {{"]
        r.append(f'graph [label = "{self.label}" bgcolor = "#bec3c6"]')
        if self.endpoints:
            ep_label = "|".join(f"<{ep}>{ep}" for ep in self.endpoints)
            r.append(f'ep_{self.node_id} [shape = record label = "{ep_label}"]')
        if self.inputs:
            in_label = "|".join(f"<{i}>{i}" for i in self.inputs)
            r.append(f'in_{self.node_id} [shape = record label = "{in_label}"]')
        if self.outputs:
            out_label = "|".join(f"<{o}>{o}" for o in self.outputs)
            r.append(f'out_{self.node_id} [shape = record label = "{out_label}"]')
        r.append("}")
        return r

    def get_ref(self, name: str) -> str:
        if name in self.endpoints:
            return f"ep_{self.node_id}:{name}"
        if name in self.inputs:
            return f"in_{self.node_id}:{name}"
        if name in self.outputs:
            return f"out_{self.node_id}:{name}"
        msg = "Invalid ref"
        raise ValueError(msg)

    def add_input(self, ep: str) -> None:
        if ep not in self.inputs and ep not in self.endpoints:
            self.inputs.append(ep)

    def add_output(self, ep: str) -> None:
        if ep not in self.outputs and ep not in self.endpoints:
            self.outputs.append(ep)

    def add_endpoint(self, ep: str) -> None:
        if ep not in self.endpoints:
            self.endpoints.append(ep)


class BaseMapper(object):
    name: str = "base"

    def __init__(self, channel: Channel):
        self.logger = PrefixLoggerAdapter(logging.getLogger("tracer"), self.name)
        self.channel = channel

    def to_dot(self, channnel: Channel) -> str:
        raise NotImplementedError

    def get_tracer(self) -> BaseTracer:
        raise NotImplementedError

    def to_dot(self) -> str:
        def get_node_key(pi: PathItem) -> str:
            parts = [str(pi.object.id)]
            if pi.input and Endpoint(object=pi.object, name=pi.input) not in endpoints:
                parts.append(pi.input)
            else:
                parts.append("")
            if pi.output and Endpoint(object=pi.object, name=pi.output) not in endpoints:
                parts.append(pi.output)
            else:
                parts.append("")
            return "|".join(parts)

        tr = self.get_tracer()
        starting = []
        endpoints = set()
        nodes = {}
        for ep in DBEndpoint.objects.filter(channel=self.channel.id):
            o, p = from_resource(ep.resource)
            if not p:
                continue
            e = Endpoint(object=o, name=p)
            endpoints.add(e)
            if ep.is_root:  # @depends on topology
                starting.append(e)
        # Trace path
        if self.channel.is_unidirectional:
            edge_style = " dir = forward"
        else:
            edge_style = ""
        edges = set()
        for ep in starting:
            last_pi = None
            last_node = None
            for pi in tr.iter_path(ep):
                # Get node
                node_key = get_node_key(pi)
                node = nodes.get(node_key)
                if not node:
                    name = " > ".join(pi.object.get_local_name_path(True))
                    model = pi.object.model.get_short_label()
                    node = Node(
                        label=f"{name}\\n{model}",
                        endpoints=[],
                        inputs=[],
                        outputs=[],
                    )
                    nodes[node_key] = node
                # Mark inputs, outputs, and endpoints
                if pi.input:
                    if Endpoint(object=pi.object, name=pi.input) in endpoints:
                        node.add_endpoint(pi.input)
                    else:
                        node.add_input(pi.input)
                if pi.output:
                    if Endpoint(object=pi.object, name=pi.output) in endpoints:
                        node.add_endpoint(pi.output)
                    elif pi.output not in node.outputs:
                        node.add_output(pi.output)
                if last_pi and last_node:
                    # Edge from previous item
                    s_ref = last_node.get_ref(last_pi.output)
                    e_ref = node.get_ref(pi.input)
                    edges.add(f"{s_ref} -- {e_ref} [{edge_style}]")
                # Internal edge
                if pi.output:
                    s_ref = node.get_ref(pi.input)
                    e_ref = node.get_ref(pi.output)
                    edges.add(f"{s_ref} -- {e_ref} [{edge_style} style = dashed]")
                last_pi = pi
                last_node = node
        r = ["graph {", "graph [rankdir = LR]"]
        for n in nodes.values():
            r.extend(n.to_dot())
        r.extend(edges)
        r.append("}")
        return "\n".join(r)
