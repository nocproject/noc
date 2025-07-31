# ----------------------------------------------------------------------
# OTNODUMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from noc.inv.models.channel import Channel
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
            label = f"{o_name}\\n{model}"
            mode = obj.get_mode()
            if mode:
                label = f"{label} [{mode}]"
            return label

        def q_disc_forward(d: str) -> str:
            try:
                _, o, i = d.split("::")
                i_c, i_n = i.split("-")
                return f"{i_c}({i_n}) \u2192 {o}"
            except ValueError:
                return d

        def q_disc_reverse(d: str) -> str:
            try:
                _, o, i = d.split("::")
                i_c, i_n = i.split("-")
                return f"{o} \u2190 {i_c}({i_n})"
            except ValueError:
                return d

        def get_client_protocol(ch: Channel) -> str | None:
            for p in ch.params:
                if p.name == "client_protocol":
                    v = p.value
                    if v.startswith("TransEth"):
                        v = v[8:] + "E"
                    return v
            return None

        def q_uni(v: str) -> str:
            if client_protocol:
                return f"{v}\n({client_protocol})"
            return v

        db_ep = DBEndpoint.objects.filter(channel=self.channel.id).first()
        controller = OTNODUController()
        path = list(controller.iter_path(Endpoint.from_resource(db_ep.resource)))
        # Client protocol
        client_protocol = get_client_protocol(self.channel)
        # Starting node
        self.add_subgraph(
            {
                "name": "cluster_start",
                "graphAttributes": {"label": node_label(path[0].object), "bgcolor": "#bec3c6"},
                "nodes": [
                    {
                        "name": "start_odu",
                        "attributes": {"label": q_uni(path[0].input), "shape": "box"},
                    },
                    {
                        "name": "start_otu",
                        "attributes": {"label": path[0].output, "shape": "box"},
                    },
                ],
            }
        )
        # Ending node
        self.add_subgraph(
            {
                "name": "cluster_end",
                "graphAttributes": {"label": node_label(path[1].object), "bgcolor": "#bec3c6"},
                "nodes": [
                    {
                        "name": "end_odu",
                        "attributes": {"label": q_uni(path[1].output), "shape": "box"},
                    },
                    {
                        "name": "end_otu",
                        "attributes": {"label": path[1].input, "shape": "box"},
                    },
                ],
            }
        )
        if path[0].channel.discriminator:
            otu = path[0].channel.discriminator.split("::")[-1]
            if client_protocol == "10GE" and otu == "OTU2":
                otu = "OTU2e"
        # Channel node
        self.add_channel("otu", channel=path[0].channel)
        self.add_edge(
            start="start_odu",
            end="start_otu",
            label=q_disc_forward(path[0].input_discriminator),
            style="dashed",
        )
        self.add_edge(
            start="end_otu",
            end="end_odu",
            label=q_disc_reverse(path[1].input_discriminator),
            style="dashed",
        )
        self.add_edge(start="start_otu", end="otu", penwidth=2)
        self.add_edge(start="otu", end="end_otu", penwidth=2)
