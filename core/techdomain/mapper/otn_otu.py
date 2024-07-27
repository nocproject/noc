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
            self.add_subgraph(
                {
                    "name": f"cluster_{name}",
                    "graphAttributes": {"label": label, "bgcolor": "#bec3c6"},
                    "nodes": [
                        {
                            "name": name,
                            "attributes": {
                                "shape": "record",
                                "label": f"{card.name}|<tx>tx|<rx>rx",
                            },
                        }
                    ],
                }
            )

        def render_path(path: List[PathItem], forward: bool) -> None:
            if not path:
                # Direct connection
                self.add_edge(
                    start="start" if forward else "end",
                    end="end" if forward else "start",
                    start_port="tx",
                    end_port="rx",
                    dir="forward",
                )
                return
            # Pass trough channels
            for pi in path:
                if pi.channel:
                    from .loader import loader as mapper_loader

                    mapper = mapper_loader[pi.channel.tech_domain.code](pi.channel)
                    start = Endpoint(object=pi.object, name=pi.input)
                    end = Endpoint(object=pi.output_object, name=pi.output)
                    ch_viz = mapper.to_viz(start=start, end=end)
                    ch_viz["name"] = "cluster_forward" if forward else "cluster_backward"
                    ch_viz["graphAttributes"]["label"] = pi.channel.name
                    ch_viz["graphAttributes"]["style"] = "dashed"
                    self.add_subgraph(ch_viz)
                    # Connect
                    if mapper.input:
                        # input
                        self.add_edge(
                            start="start" if forward else "end",
                            end=mapper.input,
                            start_port="tx",
                            end_port=mapper.input_port,
                        )
                    if mapper.output:
                        # output
                        self.add_edge(
                            start=mapper.output,
                            end="end" if forward else "start",
                            start_port=mapper.output_port,
                            end_port="rx",
                        )

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
        render_path(forward[2:-2], forward=True)
        render_path(backward[2:-2], forward=False)
