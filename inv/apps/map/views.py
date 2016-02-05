# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.map application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import urllib
import json
## Third-party modules
import tornado.httpclient
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.interface import Interface
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.mapsettings import MapSettings
from noc.inv.models.link import Link
from noc.sa.models.objectstatus import ObjectStatus
from noc.fm.models.activealarm import ActiveAlarm
from noc.lib.stencil import stencil_registry
from layout import Layout
from noc.lib.text import split_alnum
from noc.sa.interfaces.base import (ListOfParameter, IntParameter,
                                    StringParameter, DictListParameter, DictParameter)


class MapApplication(ExtApplication):
    """
    inv.net application
    """
    title = "Network Map"
    menu = "Network Map"
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

    @view("^(?P<id>[0-9a-f]{24})/data/$", method=["GET"],
          access="read", api=True)
    def api_data(self, request, id):
        def add_mo(o, external=False):
            shape = self.get_object_shape(o)
            sw, sh = self.get_shape_size(shape)
            mo[o.id] = {
                "type": "managedobject",
                "id": str(o.id),
                "name": o.name,
                "external": external,
                "shape": shape,
                "ports": [],
                "width": sw,
                "height": sh
            }
            r["nodes"] += [mo[o.id]]
            layout.set_node_size(o.id, sw, sh)
            mk = (u"managedobject", unicode(o.id))
            mos = node_settings.get(mk)
            if mos:
                layout.set_node_position(o.id, mos.x, mos.y)

        def bandwidth(speed, bandwidth):
            if speed and bandwidth:
                return min(speed, bandwidth)
            elif speed and not bandwidth:
                return speed
            elif bandwidth:
                return bandwidth
            else:
                return 0

        segment = self.get_object_or_404(NetworkSegment, id=id)
        settings = MapSettings.objects.filter(segment=id).first()
        node_settings = {}
        link_settings = {}
        layout = Layout()
        if settings:
            self.logger.debug("Using stored positions")
            layout.set_page_size(settings.width, settings.height)
            for n in settings.nodes:
                node_settings[n.type, n.id] = n
            for l in settings.links:
                link_settings[l.type, l.id] = l
        else:
            self.logger.debug("Generating positions")
        r = {
            "id": str(segment.id),
            "name": segment.name,
            "nodes": []
        }
        # Parent info
        if segment.parent:
            r["parent"] = {
                "id": str(segment.parent.id),
                "name": str(segment.parent.name)
            }
        # Nodes
        mo = {}
        for o in segment.managed_objects:
            add_mo(o, external=False)
        # Get interfaces
        ic = Interface._get_collection()
        idata = list(ic.find(
            {
                "managed_object": {
                    "$in": list(mo)
                },
                "type": {
                    "$in": ["physical", "management"]
                }
            },
            {
                "_id": 1,
                "bandwidth": 1,
                "in_speed": 1,
                "out_speed": 1
            }
        ))
        if_ids = set(i["_id"] for i in idata)
        if_bw = dict(
            (i["_id"], (
                i.get("bandwidth", 0),
                i.get("in_speed", 0),
                i.get("out_speed", 0)
            )) for i in idata
        )
        # Load links
        links = {}
        pn = 0
        for link in Link.objects.filter(interfaces__in=if_ids):
            mos = set()
            for i in link.interfaces:
                mos.add(i.managed_object)
            if len(mos) != 2:
                continue
            m0 = mos.pop()
            m1 = mos.pop()
            i0, i1 = [], []
            for i in link.interfaces:
                if i.managed_object == m0:
                    i0 += [i]
                else:
                    i1 += [i]
            if m0.id not in mo:
                add_mo(m0, external=True)
            mo[m0.id]["ports"] += [{
                "id": pn,
                "ports": [i.name for i in i0]
            }]
            if m1.id not in mo:
                add_mo(m1, external=True)
            mo[m1.id]["ports"] += [{
                "id": pn + 1,
                "ports": [i.name for i in i1]
            }]
            t_in_bw = 0
            t_out_bw = 0
            for i in i0:
                bw, in_speed, out_speed = if_bw.get(i.id, (0, 0, 0))
                t_in_bw += bandwidth(in_speed, bw)
                t_out_bw += bandwidth(out_speed, bw)
            d_in_bw = 0
            d_out_bw = 0
            for i in i1:
                bw, in_speed, out_speed = if_bw.get(i.id, (0, 0, 0))
                d_in_bw += bandwidth(in_speed, bw)
                d_out_bw += bandwidth(out_speed, bw)
            lid = (u"link", str(link.id))
            in_bw = bandwidth(t_in_bw, d_out_bw) * 1000
            out_bw = bandwidth(t_out_bw, d_in_bw) * 1000
            links[lid] = {
                "id": str(link.id),
                "type": "link",
                "method": link.discovery_method,
                "ports": [pn, pn + 1],
                # Target to source
                "in_bw": in_bw,
                # Source to target
                "out_bw": out_bw,
                # Max bandwidth
                "bw": max(in_bw, out_bw)
            }
            pn += 2
            layout.add_link(m0.id, m1.id, lid)
        # Auto-layout
        npos, lpos = layout.layout()
        # Set nodes position
        # Calculated position is the center of node
        for o in npos:
            x, y = npos[o]
            mo[o]["x"] = x
            mo[o]["y"] = y
        # Adjust link hints
        for lid in lpos:
            links[lid]["connector"] = "smooth"
            links[lid]["vertices"] = [
                {
                    "x": p["x"],
                    "y": p["y"]
                } for p in lpos[lid]
            ]
        # Override link hints with saved one
        for lid in link_settings:
            if lid not in links:
                continue
            if link_settings[lid].vertices:
                connector = link_settings[lid].connector
            else:
                connector = "normal"
            links[lid]["connector"] = connector
            links[lid]["vertices"] = [
                {
                    "x": v.x,
                    "y": v.y
                } for v in link_settings[lid].vertices]
        r["links"] = links.values()
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
                    } for n in r["nodes"]
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
        segment = self.get_object_or_404(NetworkSegment, id=id)
        data = self.deserialize(request.raw_post_data)
        data["id"] = id
        MapSettings.load_json(data, request.user.username)
        return {
            "status": True
        }

    def get_object_shape(self, object):
        if object.shape:
            # Use object's shape, if set
            sn = object.shape
        elif object.object_profile.shape:
            # Use profile's shape
            sn = object.object_profile.shape
        else:
            # Fallback to router shape
            sn = "Cisco/router"
        return sn

    def get_shape_size(self, shape):
        return stencil_registry.get_size(shape)

    @view(url="^stencils/(?P<shape>.+)/$",
        method=["GET"], access=True, api=True)
    def api_stencil(self, request, shape):
        svg = stencil_registry.get_svg(shape)
        if not svg:
            return self.response_not_found()
        else:
            return self.render_response(svg, content_type="image/svg+xml")

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
        r = {
            "id": object.id,
            "name": object.name,
            "description": object.description,
            "address": object.address,
            "platform": object.platform,
            "profile": object.profile_name,
            "external": object.segment.id != segment.id,
            "external_segment": {
                "id": str(object.segment.id),
                "name": object.segment.name
            }
        }
        return r

    @view(url="^(?P<id>[0-9a-f]{24})/info/link/(?P<link_id>[0-9a-f]{24})/$", method=["GET"],
          access="read", api=True)
    def api_info_link(self, request, id, link_id):
        segment = self.get_object_or_404(NetworkSegment, id=id)
        link = self.get_object_or_404(Link, id=link_id)
        r = {
            "id": str(link.id),
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

    @view(url="^objects_statuses/$", method=["POST"],
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
                if "ok" in a:
                    r.update([d["_id"] for d in a["result"]])
            return r

        # Mark all as unknown
        r = dict((o, self.ST_UNKNOWN) for o in objects)
        sr = ObjectStatus.get_statuses(objects)
        sa = get_alarms(objects)
        for o in sr:
            if sr[o]:
                # Check for alarms
                if o in sa:
                    r[o] = self.ST_ALARM
                else:
                    r[o] = self.ST_OK
            else:
                r[o] = self.ST_DOWN
        return r

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
            return s

        def qt(t):
            return "|".join(["%s=%s" % (v, t[v]) for v in sorted(t)])

        # Build query
        query = []
        m_objects = defaultdict(list)  # metric -> [object, ...]
        tag_id = {}
        for m in metrics:
            m_objects[m["metric"]] += [m["tags"]["object"]]
            tag_id[qt(m["tags"])] = m["id"]
        for m in m_objects:
            for o in m_objects[m]:
                query += [
                    "SELECT object, interface, last(value) "
                    "FROM \"%s\" "
                    "WHERE object='%s' "
                    "GROUP BY object, interface" % (
                        q(m),
                        q(o)
                    )
                ]
        query = ";".join(query)
        client = tornado.httpclient.HTTPClient()
        response = client.fetch(
            "http://127.0.0.1:8086/query?db=noc&q=%s" % urllib.quote(query)
        )
        data = json.loads(response.body)
        r = {}
        for qr in data["results"]:
            if not qr:
                continue
            for sv in qr["series"]:
                pid = tag_id.get(qt(sv["tags"]))
                if not pid:
                    continue
                if pid not in r:
                    r[pid] = {}
                if sv["name"] not in r[pid]:
                    r[pid][sv["name"]] = 0.0
                r[pid][sv["name"]] += sv["values"][0][-1]
        return r

    @view("^(?P<id>[0-9a-f]{24})/data/$", method=["DELETE"],
          access="write", api=True)
    def api_reset(self, request, id):
        self.get_object_or_404(NetworkSegment, id=id)
        MapSettings.objects.filter(segment=id).delete()
        return {
            "status": True
        }
