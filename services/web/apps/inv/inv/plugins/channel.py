# ---------------------------------------------------------------------
# inv.inv channel plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Iterable
from collections import defaultdict

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from noc.core.resource import resource_label
from noc.sa.interfaces.base import StringParameter, OBJECT_ID, ObjectIdParameter, BooleanParameter
from noc.core.techdomain.controller.loader import loader as controller_loader
from noc.core.techdomain.controller.base import Endpoint
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint as DBEndpoint
from noc.main.models.favorites import Favorites
from noc.sa.models.job import Job
from .base import InvPlugin


class ChannelPlugin(InvPlugin):
    name = "channel"
    js = "NOC.inv.inv.plugins.channel.ChannelPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            f"api_plugin_{self.name}_get_adhoc_list",
            self.api_get_adhoc_list,
            url=f"^(?P<id>{OBJECT_ID})/plugin/{self.name}/adhoc/$",
            method=["GET"],
        )
        self.add_view(
            f"api_plugin_{self.name}_create_adhoc",
            self.api_create_adhoc,
            url=f"^(?P<id>{OBJECT_ID})/plugin/{self.name}/adhoc/$",
            method=["POST"],
            validate={
                "channel_id": ObjectIdParameter(required=False),
                "endpoint": StringParameter(),
                "controller": StringParameter(),
                "name": StringParameter(),
                "dry_run": BooleanParameter(required=False, default=False),
            },
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
        # Place job statuses
        jobs = {job.entity: job for job in Job.iter_last_for_entities(f"ch:{x['id']}" for x in r)}
        if jobs:
            for x in r:
                job = jobs.get(f"ch:{x['id']}")
                if job:
                    x["job_id"] = str(job.id)
                    x["job_status"] = job.status
                else:
                    x["job_id"] = ""
                    x["job_status"] = ""
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
        def ep_hash(ep1: Endpoint, ep2: Endpoint) -> tuple[str, str]:
            # Only for bi-di
            r1 = ep1.as_resource()
            r2 = ep2.as_resource()
            if r1 < r2:
                return r1, r2
            return r2, r1

        def in_q(field: str, data: Iterable[str]) -> dict[str, Any]:
            d = list(data)
            if len(d) == 1:
                return {field: d[0]}
            return {field: {"$in": d}}

        def get_qualified_channels(
            endpoints: set[str], is_bidi: bool
        ) -> list[tuple[str, ObjectId]]:
            q = in_q("resource", endpoints)
            if not is_bidi:
                q["is_root"] = True
            return [
                (x["resource"], x["channel"])
                for x in DBEndpoint._get_collection().find(
                    q,
                    {"_id": 0, "resource": 1, "channel": 1},
                )
            ]

        def get_unqualified_channels(
            endpoints: set[str], is_bidi: bool
        ) -> list[tuple[str, ObjectId]]:
            q = in_q("root_resource", endpoints)
            if not is_bidi:
                q["is_root"] = True
            return [
                (x["resource"][:26], x["channel"])
                for x in DBEndpoint._get_collection().find(
                    q,
                    {"_id": 0, "resource": 1, "channel": 1},
                )
            ]

        def get_controller_proposals(controller_name: str) -> list[dict[str, Any]]:
            """
            Build proposals for controller.
            """
            r = []
            controller = controller_loader[controller_name]()
            is_bidi = controller.topology.is_bidirectional
            seen = set()
            # Query conditions
            qualified = set()
            unqualified = set()
            # For all nested objects
            for no in nested_objects:
                # Find suitable channels
                for sep, eep, params in controller.iter_adhoc_endpoints(no):
                    # Restrict to port if necessary
                    if is_xcvr and not (sep == xep or eep == xep):
                        continue
                    # For bidirectional, suppress duplicates from other direction
                    if is_bidi:
                        h = ep_hash(sep, eep)
                        if h in seen:
                            continue
                        seen.add(h)
                    # Collect query conditions
                    if sep.is_qualified and eep.is_qualified:
                        qualified.add(sep.as_resource())
                        if is_bidi:
                            qualified.add(eep.as_resource())
                    elif not sep.is_qualified and not eep.is_qualified:
                        unqualified.add(sep.as_resource())
                        if is_bidi:
                            unqualified.add(eep.as_resource())
                    else:
                        self.logger.error(
                            "Cannot handle channel combination: is_bidi=%s, sep.is_qualified=%s, eep.is_qualified=%s",
                            is_bidi,
                            sep.is_qualified,
                            eep.is_qualified,
                        )
                    # Build output record
                    r.append(
                        {
                            "start_endpoint": sep.as_resource(),
                            "start_endpoint__label": self.get_endpoint_label(sep),
                            "end_endpoint": eep.as_resource(),
                            "end_endpoint__label": self.get_endpoint_label(eep),
                            "controller": controller_name,
                        }
                    )
            # Get endpoint to channel bindings
            ep_ch: list[tuple[str, ObjectId]] = []  # [(endpoint, channel), ...]
            if qualified:
                ep_ch += get_qualified_channels(qualified, is_bidi)
            if unqualified:
                ep_ch += get_unqualified_channels(unqualified, is_bidi)
            # Get channels
            channel_name = {}
            channel_params = {}
            if ep_ch:
                for x in Channel._get_collection().find(
                    {"_id": {"$in": [e[1] for e in ep_ch]}, "controller": controller_name},
                    {"_id": 1, "name": 1, "params": 1},
                ):
                    channel_name[x["_id"]] = x["name"]
                    channel_params[x["_id"]] = x.get("params")
            # Filter out unrelevant channels of other technologies
            ch_ep = {ep: ch for ep, ch in ep_ch if ch in channel_name}
            # Enrich output
            for x in r:
                ch1 = ch_ep.get(x["start_endpoint"])
                ch2 = ch_ep.get(x["end_endpoint"])
                if not ch1 and not ch2:
                    x["status"] = "new"
                elif is_bidi:
                    if ch1 and ch2 and ch1 == ch2:
                        x["status"] = "done"
                        x["channel_id"] = str(ch1)
                        x["channel_name"] = channel_name.get(ch1) or ""
                        x["params"] = channel_params.get(ch1) or []
                    else:
                        x["status"] = "broken"
                else:
                    # Unidirectional
                    if ch1:
                        x["status"] = "done"
                        x["channel_id"] = str(ch1)
                        x["channel_name"] = channel_name.get(ch1, "")
                        x["params"] = channel_params.get(ch1) or []
                    else:
                        x["status"] = "new"
            return r

        o = self.app.get_object_or_404(Object, id=id)
        is_xcvr = o.is_xcvr and o.parent and o.parent_connection
        if is_xcvr:
            nested_objects = [o.parent]
            xep = Endpoint(object=o.parent, name=o.parent_connection)
        else:
            nested_objects = list(Object.objects.filter(id__in=o.get_nested_ids()))
        r: list[dict[str, str | bool]] = []
        # Check all controllers
        for name in controller_loader:
            r += get_controller_proposals(name)
        # Get channel statuses
        return r

    def api_create_adhoc(
        self,
        request,
        id,
        name: str,
        endpoint: str,
        controller: str,
        channel_id: str | None = None,
        dry_run: bool | None = None,
    ):
        self.app.get_object_or_404(Object, id=id)
        # Get channel
        if channel_id:
            channel = self.app.get_object_or_404(Channel, id=channel_id)
        else:
            channel = None
        # Run controller
        ep = Endpoint.from_resource(endpoint)
        ctl = controller_loader[controller]()
        ch, msg = ctl.sync_ad_hoc_channel(name=name, ep=ep, channel=channel, dry_run=dry_run)
        r = {"status": ch is not None, "msg": msg}  # @todo: Replace with message
        if ch:
            r["channel_id"] = str(ch.id)
        return r
