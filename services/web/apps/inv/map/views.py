# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.map application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import datetime
import threading
# Third-party modules
from concurrent.futures import ThreadPoolExecutor, as_completed
import six
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.interface import Interface
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.mapsettings import MapSettings
from noc.inv.models.link import Link
from noc.sa.models.objectstatus import ObjectStatus
from noc.fm.models.activealarm import ActiveAlarm
from noc.core.topology.segment import SegmentTopology
from noc.inv.models.discoveryid import DiscoveryID
from noc.maintenance.models.maintenance import Maintenance
from noc.lib.text import split_alnum
from noc.core.pm.utils import get_interface_metrics
from noc.sa.interfaces.base import (ListOfParameter, IntParameter,
                                    StringParameter, DictListParameter, DictParameter)
from noc.core.translation import ugettext as _
from noc.core.cache.decorator import cachedmethod

tags_lock = threading.RLock()


class MapApplication(ExtApplication):
    """
    inv.net application
    """
    title = _("Network Map")
    menu = _("Network Map")
    glyph = "globe"

    implied_permissions = {
        "launch": ["inv:networksegment:lookup"]
    }

    # Object statuses
    ST_UNKNOWN = 0  # Object state is unknown
    ST_OK = 1  # Object is OK
    ST_ALARM = 2  # Object is reachable, Active alarms
    ST_UNREACH = 3  # Object is unreachable due to other's object failure
    ST_DOWN = 4  # Object is down
    ST_MAINTENANCE = 32  # Maintenance bit

    # Maximum object to be shown
    MAX_OBJECTS = 300

    @view("^(?P<id>[0-9a-f]{24})/data/$", method=["GET"],
          access="read", api=True)
    def api_data(self, request, id):
        def q_mo(d):
            x = d.copy()
            if x["type"] == "managedobject":
                del x["mo"]
                x["external"] = x["id"] not in mos if is_view else x.get("role") != "segment"
                # x["id"] = str(x["id"])
            elif d["type"] == "cloud":
                del x["link"]
                x["external"] = False
            return x

        # Find segment
        segment = self.get_object_or_404(NetworkSegment, id=id)
        if segment.managed_objects.count() > self.MAX_OBJECTS:
            # Too many objects
            return {
                "id": str(segment.id),
                "name": segment.name,
                "error": _("Too many objects")
            }
        # if we set selector in segment
        is_view = segment.selector
        if is_view:
            mos = segment.selector.managed_objects.values_list("id", flat=True)
        # Load settings
        settings = MapSettings.objects.filter(segment=id).first()
        node_hints = {}
        link_hints = {}
        if settings:
            self.logger.info("Using stored positions")
            for n in settings.nodes:
                node_hints[n.id] = {
                    "type": n.type,
                    "id": n.id,
                    "x": n.x,
                    "y": n.y
                }
            for l in settings.links:
                link_hints[l.id] = {
                    "connector": l.connector if len(l.vertices) else "normal",
                    "vertices": [{"x": v.x, "y": v.y} for v in l.vertices]
                }
        else:
            self.logger.info("Generating positions")
        # Generate topology
        topology = SegmentTopology(
            segment, node_hints, link_hints,
            force_spring=request.GET.get("force") == "spring")
        topology.layout()
        # Build output
        r = {
            "id": str(segment.id),
            "max_links": int(segment.max_shown_downlinks),
            "name": segment.name,
            "caps": list(topology.caps),
            "nodes": [q_mo(x) for x in six.itervalues(topology.G.node)],
            "links": [topology.G[u][v] for u, v in topology.G.edges()]
        }
        # Parent info
        if segment.parent:
            r["parent"] = {
                "id": str(segment.parent.id),
                "name": segment.parent.name
            }
        # Save settings
        if not settings:
            self.logger.debug("Saving first-time layout")
            MapSettings.load_json({
                "id": str(segment.id),
                "nodes": [
                    {
                        "type": n["type"],
                        "id": n["id"],
                        "x": n["x"],
                        "y": n["y"]
                    } for n in r["nodes"] if n.get("x") is not None and n.get("y") is not None
                ],
                "links": [
                    {
                        "type": n["type"],
                        "id": n["id"],
                        "vertices": n.get("vertices", []),
                        "connector": n.get("connector", "normal")
                    } for n in r["links"]
                ]
            })
        return r

    @view("^(?P<id>[0-9a-f]{24})/data/$", method=["POST"],
          access="write", api=True)
    def api_save(self, request, id):
        self.get_object_or_404(NetworkSegment, id=id)
        data = self.deserialize(request.raw_post_data)
        data["id"] = id
        MapSettings.load_json(data, request.user.username)
        return {
            "status": True
        }

    @view(url="^(?P<id>[0-9a-f]{24})/info/segment/$", method=["GET"],
          access="read", api=True)
    def api_info_segment(self, request, id):
        segment = self.get_object_or_404(NetworkSegment, id=id)
        r = {
            "name": segment.name,
            "description": segment.description,
            "objects": segment.managed_objects.count()
        }
        return r

    @view(url="^(?P<id>[0-9a-f]{24})/info/managedobject/(?P<mo_id>\d+)/$", method=["GET"],
          access="read", api=True)
    def api_info_managedobject(self, request, id, mo_id):
        segment = self.get_object_or_404(NetworkSegment, id=id)
        object = self.get_object_or_404(ManagedObject, id=int(mo_id))
        s = {
            1: "telnet",
            2: "ssh",
            3: "http",
            4: "https"
        }[object.scheme]
        r = {
            "id": object.id,
            "name": object.name,
            "description": object.description,
            "address": object.address,
            "platform": object.platform.full_name if object.platform else "",
            "profile": object.profile.name,
            "external": object.segment.id != segment.id,
            "external_segment": {
                "id": str(object.segment.id),
                "name": object.segment.name
            },
            "caps": object.get_caps(),
            "console_url": "%s://%s/" % (s, object.address)
        }
        return r

    @view(url="^(?P<id>[0-9a-f]{24})/info/link/(?P<link_id>[0-9a-f]{24})/$", method=["GET"],
          access="read", api=True)
    def api_info_link(self, request, id, link_id):
        def q(s):
            if isinstance(s, unicode):
                s = s.encode("utf-8")
            return s

        self.get_object_or_404(NetworkSegment, id=id)
        link = self.get_object_or_404(Link, id=link_id)
        r = {
            "id": str(link.id),
            "name": link.name or None,
            "description": link.description or None,
            "objects": [],
            "method": link.discovery_method
        }
        o = defaultdict(list)
        for i in link.interfaces:
            o[i.managed_object] += [i]
        for mo in sorted(o, key=lambda x: x.name):
            r["objects"] += [{
                "id": mo.id,
                "name": mo.name,
                "interfaces": [
                    {
                        "name": i.name,
                        "description": i.description or None,
                        "status": i.status
                    }
                    for i in sorted(o[mo], key=lambda x: split_alnum(x.name))
                ]
            }]
        # Get link bandwidth
        mo_in = defaultdict(float)
        mo_out = defaultdict(float)
        mos = [ManagedObject.get_by_id(mo["id"]) for mo in r["objects"]]
        metric_map, last_ts = get_interface_metrics(o.keys())
        for mo in o:
            if mo not in metric_map:
                continue
            for i in o[mo]:
                if i.name not in metric_map[mo]:
                    continue
                mo_in[mo] += metric_map[mo][i.name]["Interface | Load | In"]
                mo_out[mo] += metric_map[mo][i.name]["Interface | Load | Out"]
        if len(mos) == 2:
            mo1, mo2 = mos
            r["utilisation"] = [
                int(max(mo_in[mo1], mo_out[mo2])),
                int(max(mo_in[mo2], mo_out[mo1])),
            ]
        else:
            mv = mo_in.values() + mo_out.values()
            if mv:
                r["utilisation"] = [int(max(mv))]
            else:
                r["utilisation"] = 0
        return r

    @view(url="^(?P<id>[0-9a-f]{24})/info/cloud/(?P<link_id>[0-9a-f]{24})/$", method=["GET"],
          access="read", api=True)
    def api_info_cloud(self, request, id, link_id):
        def q(s):
            if isinstance(s, unicode):
                s = s.encode("utf-8")
            return s

        self.get_object_or_404(NetworkSegment, id=id)
        link = self.get_object_or_404(Link, id=link_id)
        r = {
            "id": str(link.id),
            "name": link.name or None,
            "description": link.description or None,
            "objects": [],
            "method": link.discovery_method
        }
        o = defaultdict(list)
        for i in link.interfaces:
            o[i.managed_object] += [i]
        for mo in sorted(o, key=lambda x: x.name):
            r["objects"] += [{
                "id": mo.id,
                "name": mo.name,
                "interfaces": [
                    {
                        "name": i.name,
                        "description": i.description or None,
                        "status": i.status
                    }
                    for i in sorted(o[mo], key=lambda x: split_alnum(x.name))
                ]
            }]
        return r

    @view(
        url="^objects_statuses/$", method=["POST"],
        access="read", api=True,
        validate={
            "objects": ListOfParameter(IntParameter())
        }
    )
    def api_objects_statuses(self, request, objects):
        def get_alarms(objects):
            """
            Returns a set of objects with alarms
            """
            r = set()
            c = ActiveAlarm._get_collection()
            while objects:
                chunk, objects = objects[:500], objects[500:]
                a = c.aggregate([
                    {
                        "$match": {
                            "managed_object": {
                                "$in": chunk
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$managed_object",
                            "count": {
                                "$sum": 1
                            }
                        }
                    }
                ])
                r.update([d["_id"] for d in a])
            return r

        def get_maintenance(objects):
            """
            Returns a set of objects currently in maintenance
            :param objects:
            :return:
            """
            now = datetime.datetime.now()
            so = set(objects)
            r = set()
            for m in Maintenance._get_collection().find({
                "is_completed": False,
                "start": {
                    "$lte": now
                }
            }, {
                "_id": 0,
                "affected_objects": 1
            }):
                mo = set(r["object"] for r in m["affected_objects"])
                r |= so & mo
            return r

        # Mark all as unknown
        r = dict((o, self.ST_UNKNOWN) for o in objects)
        sr = ObjectStatus.get_statuses(objects)
        sa = get_alarms(objects)
        mo = get_maintenance(objects)
        for o in sr:
            if sr[o]:
                # Check for alarms
                if o in sa:
                    r[o] = self.ST_ALARM
                else:
                    r[o] = self.ST_OK
            else:
                r[o] = self.ST_DOWN
            if o in mo:
                r[o] |= self.ST_MAINTENANCE
        return r

    @classmethod
    @cachedmethod(
        key="managedobject-name-to-id-%s",
        lock=lambda _: tags_lock
    )
    def managedobject_name_to_id(cls, name):
        r = ManagedObject.objects.filter(name=name).values_list("id")
        if r:
            return r[0][0]
        else:
            return None

    @classmethod
    @cachedmethod(
        key="interface-tags-to-id-%s-%s",
        lock=lambda _: tags_lock
    )
    def interface_tags_to_id(cls, object_name, interface_name):
        mo = cls.managedobject_name_to_id(object_name)
        i = Interface._get_collection().find_one({
            "managed_object": mo,
            "name": interface_name
        })
        if i:
            return i["_id"]
        else:
            return None

    @view(
        url="^metrics/$", method=["POST"],
        access="read", api=True,
        validate={
            "metrics": DictListParameter(attrs={
                "id": StringParameter(),
                "metric": StringParameter(),
                "tags": DictParameter()
            })
        }
    )
    def api_metrics(self, request, metrics):
        def q(s):
            if isinstance(s, unicode):
                s = s.encode("utf-8")
            return s

        def qt(t):
            return "|".join(["%s=%s" % (v, t[v]) for v in sorted(t)])

        # Build query
        tag_id = {}  # object, interface -> id
        if_ids = {}  # id -> port id
        mlst = []  # (metric, object, interface)
        for m in metrics:
            if "object" in m["tags"] and "interface" in m["tags"]:
                if not m["tags"]["object"]:
                    continue
                try:
                    if_ids[
                        self.interface_tags_to_id(
                            m["tags"]["object"],
                            m["tags"]["interface"]
                        )
                    ] = m["id"]
                    object = ManagedObject.objects.get(name=m["tags"]["object"])
                    tag_id[object, m["tags"]["interface"]] = m["id"]
                    mlst += [(m["metric"], object, m["tags"]["interface"])]
                except KeyError:
                    pass
        # @todo: Get last values from cache
        if not mlst:
            return {}

        r = {}
        # Apply interface statuses
        for d in Interface._get_collection().find(
            {
                "_id": {
                    "$in": list(if_ids)
                }
            },
            {
                "_id": 1,
                "admin_status": 1,
                "oper_status": 1
            }
        ):
            r[if_ids[d["_id"]]] = {
                "admin_status": d.get("admin_status", True),
                "oper_status": d.get("oper_status", True)
            }
        metric_map, last_ts = get_interface_metrics([m[1] for m in mlst])
        # Apply metrics
        for rq_mo, rq_iface in tag_id:
            pid = tag_id.get((rq_mo, rq_iface))
            if not pid:
                continue
            if pid not in r:
                r[pid] = {}
            if rq_mo not in metric_map:
                continue
            if rq_iface not in metric_map[rq_mo]:
                continue
            r[pid]["Interface | Load | In"] = metric_map[rq_mo][rq_iface]["Interface | Load | In"]
            r[pid]["Interface | Load | Out"] = metric_map[rq_mo][rq_iface]["Interface | Load | Out"]

        return r

    @view("^(?P<id>[0-9a-f]{24})/data/$", method=["DELETE"],
          access="write", api=True)
    def api_reset(self, request, id):
        self.get_object_or_404(NetworkSegment, id=id)
        MapSettings.objects.filter(segment=id).delete()
        return {
            "status": True
        }

    @view(
        url="^stp/status/$", method=["POST"],
        access="read", api=True,
        validate={
            "objects": ListOfParameter(IntParameter())
        }
    )
    def api_objects_stp_status(self, request, objects):
        def get_stp_status(object_id):
            roots = set()
            blocked = set()
            object = ManagedObject.get_by_id(object_id)
            sr = object.scripts.get_spanning_tree()
            for instance in sr["instances"]:
                ro = DiscoveryID.find_object(instance["root_id"])
                if ro:
                    roots.add(ro)
                for i in instance["interfaces"]:
                    if i["state"] == "discarding" and i["role"] == "alternate":
                        iface = object.get_interface(i["interface"])
                        if iface:
                            link = iface.link
                            if link:
                                blocked.add(str(link.id))
            return object_id, roots, blocked

        r = {
            "roots": [],
            "blocked": []
        }
        futures = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for o in objects:
                futures += [executor.submit(get_stp_status, o)]
            for future in as_completed(futures):
                try:
                    obj, roots, blocked = future.result()
                    for ro in roots:
                        if ro.id not in r["roots"]:
                            r["roots"] += [ro.id]
                    r["blocked"] += blocked
                except Exception as e:
                    self.logger.error("[stp] Exception: %s", e)
        return r
