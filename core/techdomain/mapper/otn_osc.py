# ----------------------------------------------------------------------
# OTNOSCMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.inv.models.object import Object
from ..controller.base import Endpoint
from .base import BaseMapper
from ..controller.otn_osc import OTNOSCController


class OtnOscMapper(BaseMapper):
    name = "otn_osc"

    def render(
        self,
        start: Optional[Endpoint] = None,
        end: Optional[Endpoint] = None,
    ) -> None:
        def node_label(obj: Object) -> str:
            o_name = " > ".join(obj.get_local_name_path(True))
            model = obj.model.get_short_label()
            return f"{o_name}\\n{model}"

        db_ep = DBEndpoint.objects.filter(channel=self.channel.id, is_root=True).first()
        controller = OTNOSCController()
        path = list(controller.iter_path(Endpoint.from_resource(db_ep.resource)))
        self.add_subgraph(
            {
                "name": "cluster_start",
                "graphAttributes": {"label": node_label(path[0].object), "bgcolor": "#bec3c6"},
                "nodes": [
                    {
                        "name": "osc_start",
                        "attributes": {"label": path[0].input, "shape": "box"},
                    },
                    {
                        "name": "line_out",
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
                        "name": "osc_end",
                        "attributes": {"label": path[1].output, "shape": "box"},
                    },
                    {
                        "name": "line_in",
                        "attributes": {"label": path[1].input, "shape": "box"},
                    },
                ],
            }
        )

        self.add_edge(start="osc_start", end="line_out", style="dashed", dir="forward")
        self.add_edge(start="line_in", end="osc_end", style="dashed", dir="forward")
        self.add_edge(start="line_out", end="line_in", penwidth=2, dir="forward")
