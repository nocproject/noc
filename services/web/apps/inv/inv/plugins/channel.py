# ---------------------------------------------------------------------
# inv.inv channel plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Any
from collections import defaultdict

# NOC modules
from noc.inv.models.object import Object
from noc.core.techdomain.tracer.base import BaseTracer
from noc.core.resource import resource_label
from noc.sa.interfaces.base import ObjectIdParameter, StringParameter
from noc.core.techdomain.tracer.loader import loader as tracer_loader
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint
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
            validate={"object": ObjectIdParameter(), "tracer": StringParameter()},
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
            }

        nested_objects_ids = "|".join(str(o.id) for o in BaseTracer().iter_nested_objects(object))
        rx = f"^o:({nested_objects_ids}):"
        pipeline = [{"$match": {"resource": {"$regex": rx}}}, {"$group": {"_id": "$channel"}}]
        r = Endpoint._get_collection().aggregate(pipeline)
        items = [i["_id"] for i in r]
        if not items:
            return []  # No data
        endpoints = defaultdict(list)
        root_endpoints = set()
        for doc in Endpoint._get_collection().find(
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

    def object_label(self, obj: Object) -> str:
        """
        Get readable object name
        """
        local_name = obj.get_local_name_path(True)
        if local_name:
            return " | ".join(local_name)
        return obj.name

    def oblect_and_model_label(self, obj: Object) -> str:
        return f"{self.object_label(obj)} [{obj.model.get_short_label()}]"

    def api_get_adhoc_list(self, request, id):
        o = self.app.get_object_or_404(Object, id=id)
        nested_objects = list(BaseTracer().iter_nested_objects(o))
        r = []
        # Check all tracers
        for tr_name in tracer_loader:
            tr = tracer_loader[tr_name]()
            for no in nested_objects:
                if tr.is_ad_hoc_available(no):
                    r += [
                        {
                            "object": str(no.id),
                            "object__label": self.oblect_and_model_label(no),
                            "tracer": tr.name,
                        }
                    ]
        return r

    def api_create_adhoc(self, request, id, object, tracer):
        self.app.get_object_or_404(Object, id=id)
        obj = self.app.get_object_or_404(Object, id=object)
        tr = tracer_loader[tracer]()
        ch, msg = tr.sync_ad_hoc_channel(obj)
        r = {"status": ch is not None, "msg": msg}
        if ch:
            r["channel"] = str(ch.id)
        return r
