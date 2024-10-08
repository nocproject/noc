# ---------------------------------------------------------------------
# inv.inv channel plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Any, List, Tuple
from collections import defaultdict

# NOC modules
from noc.inv.models.object import Object
from noc.core.resource import resource_label, from_resource
from noc.sa.interfaces.base import StringParameter
from noc.core.techdomain.controller.loader import loader as controller_loader
from noc.core.techdomain.controller.base import Endpoint
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.main.models.favorites import Favorites
from .base import InvPlugin


class ChannelPlugin(InvPlugin):
    name = "channel"
    js = "NOC.inv.inv.plugins.channel.ChannelPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_get_adhoc_list" % self.name,
            self.api_get_adhoc_list,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/adhoc/$" % self.name,
            method=["GET"],
        )
        self.add_view(
            "api_plugin_%s_create_adhoc" % self.name,
            self.api_create_adhoc,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/adhoc/$" % self.name,
            method=["POST"],
            validate={"endpoint": StringParameter(), "controller": StringParameter()},
        )

    def get_data(self, request, object):
        def q(ch: Channel) -> Dict[str, Any]:
            def key(s: str) -> str:
                p = s.split(":")
                return ":".join(p[:2])

            ch_endpoints = endpoints[ch.id]
            from_endpoint = ""
            to_endpoint = ""
            if len(ch_endpoints) == 2:
                # p2p
                r1, r2 = ch_endpoints
                if r2 in root_endpoints:
                    r1, r2 = r2, r1
                from_endpoint = resource_label(r1)
                to_endpoint = resource_label(r2)
            elif len(ch_endpoints) > 2:
                # Multi
                hubs = defaultdict(list)
                for e in ch_endpoints:
                    hubs[key(e)].append(e)
                if len(hubs) == 2:
                    h1, h2 = list(hubs)
                    if hubs[h2][0] in root_endpoints:
                        h1, h2 = h2, h1
                    from_endpoint = f"{resource_label(h1)} + {len(hubs[h1])}"
                    to_endpoint = f"{resource_label(h2)} + {len(hubs[h2])}"
            return {
                "id": str(ch.id),
                "fav_status": str(ch.id) in fav_items,
                "name": ch.name,
                "tech_domain": str(ch.tech_domain.id),
                "tech_domain__label": ch.tech_domain.name,
                "kind": ch.kind,
                "topology": ch.topology,
                "from_endpoint": from_endpoint,
                "to_endpoint": to_endpoint,
                "discriminator": ch.discriminator or "",
            }

        if object.is_xcvr and object.parent and object.parent_connection:
            # Transceiver
            ep = f"o:{object.parent.id}:{object.parent_connection}"
            pipeline = [{"$match": {"resource": ep}}, {"$group": {"_id": "$channel"}}]
        else:
            nested = [f"o:{o_id}" for o_id in object.get_nested_ids()]
            pipeline = [
                {"$match": {"root_resource": {"$in": nested}}},
                {"$group": {"_id": "$channel"}},
            ]
        r = DBEndpoint._get_collection().aggregate(pipeline)
        items = [i["_id"] for i in r]
        if not items:
            return []  # No data
        endpoints = defaultdict(list)
        root_endpoints = set()
        for doc in DBEndpoint._get_collection().find(
            {"channel": {"$in": items}}, {"_id": 0, "resource": 1, "channel": 1, "is_root": 1}
        ):
            endpoints[doc["channel"]].append(doc["resource"])
            if doc.get("is_root"):
                root_endpoints.add(doc["resource"])
        # Get favorites
        f = Favorites.objects.filter(user=request.user.id, app="inv.channel").first()
        fav_items = set(f.favorites) if f else set()
        # Format result
        r = [q(i) for i in Channel.objects.filter(id__in=items)]
        return {"records": r}

    def get_endpoint_label(self, ep: Endpoint) -> str:
        parts = []
        local_name = ep.object.get_local_name_path(True)
        if local_name:
            parts.append(" > ".join(local_name))
        else:
            parts.append(ep.object.name)
        if ep.name:
            parts.append(f" > {ep.name}")
        parts.append(f" [{ep.object.model.get_short_label()}]")
        return "".join(parts)

    def api_get_adhoc_list(self, request, id):
        def update_proposal_status(x: Dict[str, str]):
            ch1 = ch_ep.get(x["start_endpoint"])
            ch2 = ch_ep.get(x["end_endpoint"])
            if not ch1 and not ch2:
                x["status"] = "new"
                return
            if ch1 and ch2 and ch1 == ch2:
                x["status"] = "done"
                return
            x["status"] = "broken"

        def ep_hash(controller: str, ep1: Endpoint, ep2: Endpoint) -> Tuple[str, str, str]:
            r1 = ep1.as_resource()
            r2 = ep2.as_resource()
            if r1 < r2:
                return controller, r1, r2
            return controller, r2, r1

        o = self.app.get_object_or_404(Object, id=id)
        is_xcvr = o.is_xcvr and o.parent and o.parent_connection
        if is_xcvr:
            nested_objects = [o.parent]
            xep = Endpoint(object=o.parent, name=o.parent_connection)
        else:
            nested_objects = list(Object.objects.filter(id__in=o.get_nested_ids()))
        r: List[Dict[str, str]] = []
        # Check all cotrollers
        seen = set()
        for controller_name in controller_loader:
            controller = controller_loader[controller_name]()
            for no in nested_objects:
                for sep, eep in controller.iter_adhoc_endpoints(no):
                    if is_xcvr and not (sep == xep or eep == xep):
                        continue
                    if controller.topology.is_bidirectional:
                        # Supress duplicates in other direction
                        h = ep_hash(controller.name, sep, eep)
                        if h in seen:
                            continue
                        seen.add(h)
                    r += [
                        {
                            "start_endpoint": sep.as_resource(),
                            "start_endpoint__label": self.get_endpoint_label(sep),
                            "end_endpoint": eep.as_resource(),
                            "end_endpoint__label": self.get_endpoint_label(eep),
                            "controller": controller.name,
                        }
                    ]
        # Get channel endpoints
        endpoints = {x["start_endpoint"] for x in r}
        endpoints.update(x["end_endpoint"] for x in r)
        qualified = [x for x in endpoints if len(x) > 27]
        unqualified = [x for x in endpoints if len(x) == 26]
        ch_ep = {}
        if qualified:
            ch_ep.update(
                {
                    x["resource"]: x["channel"]
                    for x in DBEndpoint._get_collection().find(
                        {"resource": {"$in": qualified}},
                        {"_id": 0, "resource": 1, "channel": 1},
                    )
                }
            )
        if unqualified:
            ch_ep.update(
                {
                    x["resource"][:26]: x["channel"]
                    for x in DBEndpoint._get_collection().find(
                        {"root_resource": {"$in": unqualified}},
                        {"_id": 0, "resource": 1, "channel": 1},
                    )
                }
            )
        # Update statuses
        for x in r:
            update_proposal_status(x)
        return r

    def api_create_adhoc(self, request, id, endpoint, controller):
        self.app.get_object_or_404(Object, id=id)
        o, n = from_resource(endpoint)
        ep = Endpoint(object=o, name=n or "")
        tr = controller_loader[controller]()
        ch, msg = tr.sync_ad_hoc_channel(ep)
        r = {"status": ch is not None, "msg": msg}
        if ch:
            r["channel"] = str(ch.id)
        return r
