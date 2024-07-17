# ----------------------------------------------------------------------
# OTNODUMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.inv.models.object import Object
from ..tracer.base import Endpoint
from .base import BaseMapper
from ..tracer.otn_odu import OTNODUTracer


class DWDMOdUMapper(BaseMapper):
    name = "otn_odu"

    def to_dot(self) -> str:
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
        start = Endpoint.from_resource(db_ep.resource)
        tr = OTNODUTracer()
        path = list(tr.iter_path(start))
        # @todo: Check path length
        r = [
            "graph {",
            "  graph [rankdir = LR]",
            "  subgraph cluster_start {",
            f'   graph [label = "{node_label(path[0].object)}" bgcolor = "#bec3c6"]',
            f'   start_odu [ label = "{path[0].input}" shape = box]',
            f'   start_otu [ label = "{path[0].output}" shape = box]',
            "  }",
            "  subgraph cluster_end {",
            f'   graph [label = "{node_label(path[1].object)}" bgcolor = "#bec3c6"]',
            f'   end_odu [ label = "{path[1].output}" shape = box]',
            f'   end_otu [ label = "{path[1].input}" shape = box]',
            "  }",
            f'  start_otu -- start_odu [label = "{q_disc(path[0].input_discriminator)}"]',
            f'  end_otu -- end_odu [label = "{q_disc(path[1].input_discriminator)}"]',
            f'  start_otu -- end_otu [label = "{path[0].channel.name}"]' "}",
        ]
        print("\n".join(r))
        return "\n".join(r)
