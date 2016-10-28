# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm heatmap
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## Third-party modules
import cachetools
import geojson
## NOC modules
from base import BaseCard
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem
from noc.gis.models.layer import Layer
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection


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

    def get_data(self):
        return {}

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
        active_layers= [l for l in self.get_pop_layers() if l.min_zoom <= zoom and l.max_zoom >= zoom]
        alarms = []
        services = {}
        subscribers = {}
        segments = set()
        if self.current_user.is_superuser:
            qs = ActiveAlarm.objects.all()
        else:
            qs = ActiveAlarm.objects.filter(adm_path__in=self.get_user_domains())
        for a in qs.only("id", "managed_object", "direct_subscribers", "direct_services"):
            mo = a.managed_object
            s_sub = SummaryItem.items_to_dict(a.direct_subscribers)
            s_service = SummaryItem.items_to_dict(a.direct_services)
            if mo.x and mo.y:
                w = ServiceSummary.get_weight({
                    "subscriber": s_sub,
                    "service": s_service
                })
                # @todo: Check west/south hemisphere
                if west <= mo.x <= east and south <= mo.y <= north:
                    segments.add(mo.segment)
            else:
                w = 0
            alarms += [{
                "alarm_id": str(a.id),
                "managed_object": mo.name,
                "x": mo.x,
                "y": mo.y,
                "w": max(w, 1)
            }]
            update_dict(services, s_service)
            update_dict(subscribers, s_sub)
        links = None
        if segments and active_layers:
            seen = set()
            for s in segments:
                seen |= set(s.managed_objects.values_list("x", "y"))
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
                    "$geoWithin": {
                        "$geometry": bbox
                    }
                }
            }, {
                "_id": 0,
                "connection": 1,
                "line": 1
            }):
                for c in d["line"]["coordinates"]:
                    if tuple(c) in seen:
                        lines += [d["line"]]
            if lines:
                links = geojson.FeatureCollection(features=lines)
        return {
            "alarms": alarms,
            "summary": self.f_glyph_summary({
                "service": services,
                "subscriber": subscribers
            }),
            "links": links
        }
