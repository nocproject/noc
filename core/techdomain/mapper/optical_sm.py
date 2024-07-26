# ----------------------------------------------------------------------
# OpticalSMMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Optional, Dict, Any

# Python modules
from noc.core.channel.types import ChannelTopology
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.core.resource import from_resource
from ..controller.base import BaseController, Endpoint, PathItem
from .base import BaseMapper, Node
from ..controller.optical_dwdm import OpticalDWDMController


class OpticalSMMapper(BaseMapper):
    name = "optical_sm"

    def render(
        self,
        start: Optional[Endpoint] = None,
        end: Optional[Endpoint] = None,
    ) -> None:
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

        controller = self.get_controller()
        starting = []
        endpoints = set()
        nodes = {}
        used_by = defaultdict(list)  # endpoint resource -> (ch name, discriminator)
        endpoint_nodes = {}  # endpoint resource -> node
        query = {"channel": self.channel.id}
        if start and not end:
            query["resource"] = start.as_resource()
        elif not start and end:
            query["resource"] = end.as_resource()
        elif start and end:
            query["resource__in"] = [start.as_resource(), end.as_resource()]
        for ep in DBEndpoint.objects.filter(**query):
            o, p = from_resource(ep.resource)
            if not p:
                continue
            e = Endpoint(object=o, name=p)
            endpoints.add(e)
            if self.channel.is_unidirectional:
                if ep.is_root:
                    starting.append(e)
            else:
                starting.append(e)
            if not start and ep.used_by:
                res = e.as_resource()
                for u in ep.used_by:
                    used_by[res].append((u.channel.name, u.discriminator))
        # Edge attributes
        if self.channel.is_unidirectional:
            edge_attrs = {"dir": "forward"}
        else:
            edge_attrs = {}
        internal_edge_attrs = edge_attrs.copy() if edge_attrs else {}
        internal_edge_attrs["style"] = "dashed"
        # Trace path
        for ep in starting:
            last_pi = None
            last_node = None
            for pi in controller.iter_path(ep):
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
                    ee = Endpoint(object=pi.object, name=pi.input)
                    if ee in endpoints:
                        node.add_endpoint(pi.input)
                        endpoint_nodes[ee.as_resource()] = node
                        if start and ee.as_resource() == start.as_resource():
                            self.input = node.get_ref(pi.input)
                            self.input_port = pi.input
                    else:
                        node.add_input(pi.input)
                if pi.output:
                    ee = Endpoint(object=pi.object, name=pi.output)
                    if ee in endpoints:
                        node.add_endpoint(pi.output)
                        endpoint_nodes[ee.as_resource()] = node
                        if end and ee.as_resource() == end.as_resource():
                            self.output = node.get_ref(pi.output)
                            self.output_port = pi.output
                    elif pi.output not in node.outputs:
                        node.add_output(pi.output)
                if last_pi and last_node:
                    # Edge from previous item
                    self.add_edge(
                        start=last_node.get_ref(last_pi.output),
                        end=node.get_ref(pi.input),
                        start_port=last_pi.output,
                        end_port=pi.input,
                        **edge_attrs,
                    )
                # Internal edge
                if pi.output:
                    self.add_edge(
                        start=node.get_ref(pi.input),
                        end=node.get_ref(pi.output),
                        start_port=pi.input,
                        end_port=pi.output,
                        **internal_edge_attrs,
                    )
                last_pi = pi
                last_node = node
        # Render
        self.add_subgraphs(n.to_viz() for n in nodes.values())
        # Apply used by
        for x, ep_resource in enumerate(used_by):
            node = endpoint_nodes[ep_resource]
            for y, (ch, _discriminator) in enumerate(used_by[ep_resource]):
                k = f"u_{x}_{y}"
                _, _, n = ep_resource.split(":", 2)
                self.add_node(
                    {"name": k, "attributes": {"shape": "hexagon", "label": ch, "style": "dashed"}}
                )
                self.add_edge(start=k, end=node.get_ref(n), end_port=n)

    def get_controller(self) -> BaseController:
        if self.channel.topology == ChannelTopology.UBUNCH.value:
            return OpticalDWDMController()
        raise NotImplementedError()
