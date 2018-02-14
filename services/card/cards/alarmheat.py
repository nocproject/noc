# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alarm heatmap
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
from collections import defaultdict
# Third-party modules
import cachetools
import geojson
# NOC modules
from .base import BaseCard
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem
from noc.gis.models.layer import Layer
from noc.inv.models.objectconnection import ObjectConnection
from noc.maintenance.models.maintenance import Maintenance
from noc.config import config


class AlarmHeatCard(BaseCard):
    name = "alarmheat"
    card_css = [
        "/ui/pkg/leaflet/leaflet.css",
        "/ui/card/css/alarmheat.css"
    ]
    card_js = [
        "/ui/pkg/leaflet/leaflet.js",
        "/ui/pkg/leaflet.heat/leaflet-heat.js",
        "/ui/card/js/alarmheat.js"
    ]

    default_template_name = "alarmheat"

    _layer_cache = {}
    TOOLTIP_LIMIT = config.card.alarmheat_tooltip_limit

    def get_data(self):
        p = self.current_user.get_profile()
        return {
            "maintenance": 0,
            "lon": p.heatmap_lon or 0,
            "lat": p.heatmap_lat or 0,
            "zoom": p.heatmap_zoom or 0
        }

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_layer_cache"))
    def get_pop_layers(cls):
        return list(
            Layer.objects.filter(code__startswith="pop_")
        )

    def get_ajax_data(self, **kwargs):
        def update_dict(d, s):
            for k in s:
                if k in d:
                    d[k] += s[k]
                else:
                    d[k] = s[k]

        zoom = int(self.handler.get_argument("z"))
        west = float(self.handler.get_argument("w"))
        east = float(self.handler.get_argument("e"))
        north = float(self.handler.get_argument("n"))
        south = float(self.handler.get_argument("s"))
        ms = int(self.handler.get_argument("maintenance"))
        active_layers = [l for l in self.get_pop_layers() if l.min_zoom <= zoom <= l.max_zoom]
        alarms = []
        services = {}
        subscribers = {}
        t_data = defaultdict(list)
        if self.current_user.is_superuser:
            qs = ActiveAlarm.objects.all()
        else:
            qs = ActiveAlarm.objects.filter(adm_path__in=self.get_user_domains())
        if ms == 0:
            # Filter out equipment under maintenance
            qs = qs.filter(managed_object__nin=Maintenance.currently_affected())
        for a in qs.only("id", "managed_object", "direct_subscribers", "direct_services"):
            s_sub, s_service = {}, {}
            if a.direct_subscribers:
                s_sub = SummaryItem.items_to_dict(a.direct_subscribers)
            if a.direct_services:
                s_service = SummaryItem.items_to_dict(a.direct_services)
            mo = a.managed_object
            if not mo:
                continue
            if mo.x and mo.y:
                w = ServiceSummary.get_weight({
                    "subscriber": s_sub,
                    "service": s_service
                })
                # @todo: Should we add the object's weight to summary?
                # @todo: Check west/south hemisphere
                if active_layers and west <= mo.x <= east and south <= mo.y <= north:
                    t_data[mo.x, mo.y] += [(mo, w)]
            else:
                w = 0
            alarms += [{
                "alarm_id": str(a.id),
                "managed_object": mo.name,
                "x": mo.x,
                "y": mo.y,
                "w": max(w, 1)
            }]
            if s_service:
                update_dict(services, s_service)
            if s_sub:
                update_dict(subscribers, s_sub)
        links = None
        o_seen = set()
        points = None
        o_data = {}
        if t_data and active_layers:
            # Create lines
            bbox = geojson.Polygon([[
                [west, north],
                [east, north],
                [east, south],
                [west, south],
                [west, north]
            ]])
            lines = []
            for d in ObjectConnection._get_collection().find({
                "type": "pop_link",
                "layer": {
                    "$in": [l.id for l in active_layers]
                },
                "line": {
                    "$geoIntersects": {
                        "$geometry": bbox
                    }
                }
            }, {
                "_id": 0,
                "connection": 1,
                "line": 1
            }):
                for c in d["line"]["coordinates"]:
                    if tuple(c) in t_data:
                        for c in d["line"]["coordinates"]:
                            tc = tuple(c)
                            o_data[tc] = t_data.get(tc, [])
                        o_seen.add(tuple(c))
                        lines += [d["line"]]
                        break
            if lines:
                links = geojson.FeatureCollection(features=lines)
            # Create points
            points = []
            for x, y in o_data:
                mos = {}
                for mo, w in o_data[x, y]:
                    if mo not in mos:
                        mos[mo] = w
                mos = sorted(
                    mos,
                    key=lambda z: mos[z],
                    reverse=True
                )[:self.TOOLTIP_LIMIT]
                points += [
                    geojson.Feature(
                        geometry=geojson.Point(
                            coordinates=[x, y]
                        ),
                        properties={
                            "alarms": len(t_data[x, y]),
                            "objects": [{
                                "id": mo.id,
                                "name": mo.name,
                                "address": mo.address
                            } for mo in mos]
                        }
                    )
                ]
            points = geojson.FeatureCollection(features=points)
        return {
            "alarms": alarms,
            "summary": self.f_glyph_summary({
                "service": services,
                "subscriber": subscribers
            }),
            "links": links,
            "pops": points
        }
