# ----------------------------------------------------------------------
# OTNOTUMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Optional, List

# Python modules
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from ..controller.base import Endpoint, PathItem
from .base import BaseMapper
from ..controller.otn_otu import OTNOTUController


class DWDMOTUMapper(BaseMapper):
    name = "otn_otu"

    def render(
        self,
        start: Optional[Endpoint] = None,
        end: Optional[Endpoint] = None,
    ) -> Dict[str, Any]:
        def add_termination_node(name: str, card: Endpoint) -> Dict[str, Any]:
            o_name = " > ".join(card.object.get_local_name_path(True))
            model = card.object.model.get_short_label()
            label = f"{o_name}\n{model}"
            mode = card.object.get_mode()
            if mode:
                label = f"{label} [{mode}]"
            ports = "<tx>tx|<rx>rx" if name == "start" else "<rx>rx|<tx>tx"
            self.add_subgraph(
                {
                    "name": f"cluster_{name}",
                    "graphAttributes": {
                        "label": label,
                        "bgcolor": "#bec3c6",
                    },
                    "nodes": [
                        {
                            "name": name,
                            "attributes": {
                                "shape": "record",
                                "label": f"{card.name}|{ports}",
                                "class": self.SELECTABLE_CLASS,
                                "id": self.get_interaction_tag(resource=card.object.as_resource()),
                                "tooltip": "",
                            },
                        }
                    ],
                }
            )

        def render_path(path: List[PathItem], forward: bool):
            """
            Append path to map.

            Returns:
                Tuple of names of first and last node.
            """
            # Pass trough channels
            prefix = "f" if forward else "b"
            nodes: List[str] = []
            for n, pi in enumerate(path):
                if pi.channel:
                    name = f"{prefix}-{n}"
                    self.add_channel(name, channel=pi.channel)
                    nodes.append(name)
            if len(nodes) > 1:
                # Connect nodes between each other
                for f, t in zip(nodes, nodes[1:]):
                    self.add_edge(start=f, end=t, penwidth=2)
            if forward:
                self.add_edge(
                    start="start", end=nodes[0], start_port="tx", penwidth=2, dir="forward"
                )
                self.add_edge(start=nodes[-1], end="end", end_port="rx", penwidth=2, dir="forward")
            else:
                self.add_edge(end="end", start=nodes[-1], end_port="tx", penwidth=2, dir="back")
                self.add_edge(end=nodes[0], start="start", start_port="rx", penwidth=2, dir="back")

        controller = OTNOTUController()
        paths = []
        for db_ep in DBEndpoint.objects.filter(channel=self.channel.id):
            ep = Endpoint.from_resource(db_ep.resource)
            paths.append(list(controller.iter_path(ep)))
        if len(paths) != 2:
            raise ValueError("Mismatched paths")
        forward, backward = paths
        # Starting node
        card = Endpoint(object=forward[0].object, name=forward[0].output)
        add_termination_node("start", card)
        # Ending node
        card = Endpoint(object=forward[-1].object, name=forward[-1].input)
        add_termination_node("end", card)
        # Render paths
        if len(forward) == 4 and len(backward) == 4:
            # Direct connection
            self.add_edge(
                start="start",
                end="end",
                start_port="tx",
                end_port="rx",
            )
            self.add_edge(
                start="end",
                end="start",
                start_port="tx",
                end_port="rx",
            )
        else:
            render_path(forward[2:-2], forward=True)
            render_path(backward[2:-2], forward=False)
