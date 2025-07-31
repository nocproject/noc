# ----------------------------------------------------------------------
# BaseMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import List, Iterable, Optional, Dict, Any

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.inv.models.channel import Channel
from noc.core.facade.interaction import (
    Interaction,
    InteractionAction,
    InteractionEvent,
    InteractionItem,
)
from ..controller.base import Endpoint


@dataclass
class Node(object):
    label: str
    endpoints: List[str]
    inputs: List[str]
    outputs: List[str]

    @property
    def node_id(self) -> str:
        return str(id(self))

    def to_viz(self) -> Dict[str, Any]:
        """
        Render node as subgraph.
        """

        def get_node(node_id: str, names: Iterable[str]) -> Dict[str, Any]:
            label = "|".join(f"<{n}>{n}" for n in names)
            return {
                "name": node_id,
                "attributes": {
                    "shape": "record",
                    "label": label,
                },
            }

        r = {
            "name": f"cluster_{self.node_id}",
            "graphAttributes": {"bgcolor": "#bec3c6", "label": self.label},
            "nodes": [],
        }
        if self.endpoints:
            r["nodes"].append(get_node(f"ep_{self.node_id}", self.endpoints))
        if self.inputs:
            r["nodes"].append(get_node(f"in_{self.node_id}", self.inputs))
        if self.outputs:
            r["nodes"].append(get_node(f"out_{self.node_id}", self.outputs))
        return r

    def get_ref(self, name: str) -> str:
        if name in self.endpoints:
            return f"ep_{self.node_id}"
        if name in self.inputs:
            return f"in_{self.node_id}"
        if name in self.outputs:
            return f"out_{self.node_id}"
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
    CHANNEL_SHAPE = "octagon"
    SELECTABLE_CLASS = "ch-selectable"

    def __init__(self, channel: Channel):
        self.logger = PrefixLoggerAdapter(logging.getLogger("tracer"), self.name)
        self.channel = channel
        self.input: Optional[str] = None
        self.input_port: Optional[str] = None
        self.output: Optional[str] = None
        self.output_port: Optional[str] = None
        self.g = self.get_graph()
        self._seen_edges = set()

    def render(
        self,
        start: Optional[Endpoint] = None,
        end: Optional[Endpoint] = None,
    ) -> None:
        """
        Render graph
        """
        raise NotImplementedError

    def to_viz(
        self,
        start: Optional[Endpoint] = None,
        end: Optional[Endpoint] = None,
    ) -> Dict[str, Any]:
        """
        Render graph and get vis-js JSON
        """
        self.set_label(f"{self.channel.name} [{self.channel.tech_domain.name}]")
        self.render(start, end)
        return self.g

    @staticmethod
    def get_graph() -> Dict[str, Any]:
        """
        Generate graph template
        """
        return {
            "graphAttributes": {
                "label": "",
                "bgcolor": "",
                "rankdir": "LR",
            },
            "directed": False,
            "nodes": [],
            "edges": [],
            "subgraphs": [],
        }

    def set_rankdir(self, rankdir: str) -> None:
        self.g["graphAttributes"]["rankdir"] = rankdir

    def set_label(self, label: str) -> None:
        self.g["graphAttributes"]["label"] = label
        self.g["graphAttributes"]["labelloc"] = "top"

    def add_edge(
        self,
        start: str,
        end: str,
        start_port: Optional[str] = None,
        end_port: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Note the edge starts from tail and goes to the head
        r = {
            "head": end,
            "tail": start,
        }
        if start_port or end_port or kwargs:
            r["attributes"] = {}
        if start_port:
            r["attributes"]["tailport"] = start_port
        if end_port:
            r["attributes"]["headport"] = end_port
        if kwargs:
            r["attributes"].update(kwargs)
        h = str(r)
        if h in self._seen_edges:
            return
        self.g["edges"].append(r)
        self._seen_edges.add(h)

    def add_node(self, node: Dict[str, Any]) -> None:
        """Add node to graph."""
        self.g["nodes"].append(node)

    def add_nodes(self, iter: Iterable[Dict[str, Any]]) -> None:
        """Add nodes from iterable."""
        self.g["nodes"].extend(iter)

    def add_subgraph(self, node: Dict[str, Any]) -> None:
        """Add subgraph to graph."""
        self.g["subgraphs"].append(node)

    def add_subgraphs(self, iter: Iterable[Dict[str, Any]]) -> None:
        """Add nodes from iterable."""
        self.g["subgraphs"].extend(iter)

    def add_channel(self, name: str, *, channel: Channel, is_client: bool = False) -> None:
        """
        Add channel.

        Args:
            name: Name on the graph.
            channel: Channel instance.
            is_client: True, if the channel uses current one.
        """
        attrs = {
            "shape": self.CHANNEL_SHAPE,
            "label": f"{channel.name}\n{channel.tech_domain.name}",
            "class": self.SELECTABLE_CLASS,
            "id": self.get_interaction_tag(resource=channel.as_resource()),
            "tooltip": channel.name,
        }
        if is_client:
            attrs["style"] = "dashed"
        self.add_node(
            {
                "name": name,
                "attributes": attrs,
            }
        )

    def get_interaction_tag(self, resource: str) -> str:
        """Encode data-interaction tag."""
        return Interaction(
            actions=[
                InteractionItem(
                    event=InteractionEvent.CLICK,
                    action=InteractionAction.INFO,
                    resource=resource,
                )
            ]
        ).to_str()

    def reverse_graph(self, g: dict[str, Any]):
        """Reverse direction of the graph."""

        def swap(d: dict[str, str], x: str, y: str) -> None:
            """
            Swap labels in dir
            """
            old_x = d.get(x)
            old_y = d.get(y)
            if old_x is None and old_y is not None:
                del d[y]
            if old_y is None and old_x is not None:
                del d[x]
            if old_x is not None:
                d[y] = old_x
            if old_y is not None:
                d[x] = old_y

        if "edges" not in g:
            return
        for edge in g["edges"]:
            if "attributes" not in edge:
                edge["attributes"] = {}
            attrs = edge["attributes"]
            direction = attrs.get("dir") or "forward"
            # Swap direction
            attrs["dir"] = "back" if direction == "forward" else "forward"
            # head <-> tail
            swap(edge, "head", "tail")
            # headport <-> tailport
            swap(attrs, "headport", "tailport")
