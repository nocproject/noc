# ----------------------------------------------------------------------
# OTNODUMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Optional

# NOC modules
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.inv.models.object import Object
from ..controller.base import Endpoint
from .base import BaseMapper
from ..controller.otn_odu import OTNODUController


class DWDMOdUMapper(BaseMapper):
    name = "otn_odu"

    def render(
        self,
        start: Optional[Endpoint] = None,
        end: Optional[Endpoint] = None,
    ) -> None:
        def node_label(obj: Object) -> str:
            o_name = " > ".join(obj.get_local_name_path(True))
            model = obj.model.get_short_label()
            return f"{o_name}\\n{model}"

        def q_disc(d: str) -> str:
            try:
                _, o, i = d.split("::")
                i_c, i_n = i.split("-")
                return f"{i_c}({i_n}) -> {o}"
            except ValueError:
                return d

        db_ep = DBEndpoint.objects.filter(channel=self.channel.id).first()
        controller = OTNODUController()
        path = list(controller.iter_path(Endpoint.from_resource(db_ep.resource)))
        self.add_subgraph(
            {
                "name": "cluster_start",
                "graphAttributes": {"label": node_label(path[0].object), "bgcolor": "#bec3c6"},
                "nodes": [
                    {
                        "name": "start_odu",
                        "attributes": {"label": path[0].input, "shape": "box"},
                    },
                    {
                        "name": "start_otu",
                        "attributes": {"label": path[0].output, "shape": "box"},
                    },
                ],
            }
        )
        self.add_subgraph(
            {
                "name": "cluster_end",
                "graphAttributes": {"label": node_label(path[1].object), "bgcolor": "#bec3c6"},
                "nodes": [
                    {
                        "name": "end_odu",
                        "attributes": {"label": path[1].output, "shape": "box"},
                    },
                    {
                        "name": "end_otu",
                        "attributes": {"label": path[1].input, "shape": "box"},
                    },
                ],
            }
        )
        self.add_edge(start="start_odu", end="start_otu", label=q_disc(path[0].input_discriminator))
        self.add_edge(start="end_otu", end="end_odu", label=q_disc(path[1].input_discriminator))
        self.add_edge(start="start_otu", end="end_otu", label=path[0].channel.name)
