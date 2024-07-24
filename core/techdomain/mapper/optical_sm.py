# ----------------------------------------------------------------------
# OpticalSMMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Optional

# Python modules
from noc.core.channel.types import ChannelTopology
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.core.resource import from_resource
from ..controller.base import BaseController, Endpoint, PathItem
from .base import BaseMapper, Node
from ..controller.optical_dwdm import OpticalDWDMController


class OpticalSMMapper(BaseMapper):
    name = "optical_sm"

    def get_controller(self) -> BaseController:
        if self.channel.topology == ChannelTopology.UBUNCH.value:
            return OpticalDWDMController()
        raise NotImplementedError()

    def to_dot(
        self,
        start: Optional[Endpoint] = None,
        end: Optional[Endpoint] = None,
        connect_input: Optional[str] = None,
        connect_output: Optional[str] = None,
    ) -> str:
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

        tr = self.get_controller()
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
            if ep.is_root:  # @depends on topology
                starting.append(e)
            if not start and ep.used_by:
                res = e.as_resource()
                for u in ep.used_by:
                    used_by[res].append((u.channel.name, u.discriminator))
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
                    ee = Endpoint(object=pi.object, name=pi.input)
                    if ee in endpoints:
                        node.add_endpoint(pi.input)
                        endpoint_nodes[ee.as_resource()] = node
                        if start and connect_input and ee.as_resource() == start.as_resource():
                            edges.add(f"{connect_input} -- {node.get_ref(pi.input)} [{edge_style}]")
                    else:
                        node.add_input(pi.input)
                if pi.output:
                    ee = Endpoint(object=pi.object, name=pi.output)
                    if ee in endpoints:
                        node.add_endpoint(pi.output)
                        endpoint_nodes[ee.as_resource()] = node
                        if end and connect_output and ee.as_resource() == end.as_resource():
                            edges.add(
                                f"{node.get_ref(pi.output)} -- {connect_output} [{edge_style}]"
                            )
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
        if start:
            r = []
        else:
            r = ["graph {", "graph [rankdir = LR]"]
        for n in nodes.values():
            r.extend(n.to_dot())
        r.extend(edges)
        # Apply used by
        for x, ep_resource in enumerate(used_by):
            node = endpoint_nodes[ep_resource]
            for y, (ch, discriminator) in enumerate(used_by[ep_resource]):
                k = f"u_{x}_{y}"
                r.append(f'  {k} [ label = "{ch}" shape = parallelogram]')
                _, _, n = ep_resource.split(":", 2)
                ref = node.get_ref(n)
                r.append(f"  {k} -- {ref}")
        if start:
            pass
        else:
            r.append("}")
        return "\n".join(r)
