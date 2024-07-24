# ----------------------------------------------------------------------
# OTNOTUMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable

# Python modules
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from ..controller.base import Endpoint
from .base import BaseMapper
from ..controller.otn_otu import OTNOTUController


class DWDMOTUMapper(BaseMapper):
    name = "otn_otu"

    def to_dot(self) -> str:
        def render_end_node(name: str, card: Endpoint, xcvr: Endpoint) -> Iterable[str]:
            o_name = " > ".join(card.object.get_local_name_path(True))
            model = card.object.model.get_short_label()
            label = f"{o_name}\\n{model}"
            r = [
                f"  subgraph cluster_{name} {{",
                f'    graph [label = "{label}" bgcolor = "#bec3c6"]',
            ]
            if name == "start":
                label = f"{card.name}|<tx>tx|<rx>rx"
            else:
                label = f"{card.name}|<rx>rx|<tx>tx"
            r.append(f'    {name} [ shape = record label = "{label}"]')
            r.append("  }")
            yield from r

        tr = OTNOTUController()
        paths = []
        for db_ep in DBEndpoint.objects.filter(channel=self.channel.id):
            ep = Endpoint.from_resource(db_ep.resource)
            paths.append(list(tr.iter_path(ep)))
        # @todo: Check path length

        r = ["graph {", "  graph [rankdir = LR]"]
        forward, backward = paths
        # Starting node
        card = Endpoint(object=forward[0].object, name=forward[0].output)
        xcvr = Endpoint(object=forward[1].object, name="")
        r.extend(render_end_node("start", card, xcvr))
        # Ending node
        card = Endpoint(object=forward[-1].object, name=forward[-1].input)
        xcvr = Endpoint(object=forward[-2].object, name="")
        r.extend(render_end_node("end", card, xcvr))
        # Render forward path
        rp = forward[2:-2]
        if rp:
            # Pass trough channels
            for pi in rp:
                if pi.channel:
                    from .loader import loader as mapper_loader

                    inner_mapper = mapper_loader[pi.channel.tech_domain.code](pi.channel)
                    r += [
                        f"subgraph cluster_ch_{pi.channel.id} {{",
                        f'  graph [ label = "{pi.channel.name}" style = dashed ]',
                    ]
                    start = Endpoint(object=pi.object, name=pi.input)
                    end = Endpoint(object=pi.output_object, name=pi.output)
                    r.append(
                        inner_mapper.to_dot(
                            start=start, end=end, connect_input="start:tx", connect_output="end:rx"
                        )
                    )
                    r.append("}")
        else:
            # Direct connection
            r.append("  start:rx -- end:rx [ dir = forward ]")
        # Render backward path
        rp = backward[2:-2]
        if rp:
            # Pass trough channels
            for pi in rp:
                if pi.channel:
                    from .loader import loader as mapper_loader

                    inner_mapper = mapper_loader[pi.channel.tech_domain.code](pi.channel)
                    r += [
                        f"subgraph cluster_ch_{pi.channel.id} {{",
                        f'  graph [ label = "{pi.channel.name}" style = dashed ]',
                    ]
                    start = Endpoint(object=pi.object, name=pi.input)
                    end = Endpoint(object=pi.output_object, name=pi.output)
                    r.append(
                        inner_mapper.to_dot(
                            start=start, end=end, connect_input="end:tx", connect_output="start:rx"
                        )
                    )
                    r.append("}")
        else:
            r.append("  end:rx -- start:rx [ dir = forward ]")
        r.append("}")
        print("\n".join(r))
        return "\n".join(r)
