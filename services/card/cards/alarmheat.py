# ---------------------------------------------------------------------
# Alarm heatmap
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from collections import defaultdict
from typing import Dict, List, Tuple, Any

# Third-party modules
import cachetools
import geojson

# NOC modules
from .base import BaseCard
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import ServiceSummary
from noc.sa.models.useraccess import UserAccess
from noc.gis.models.layer import Layer
from noc.inv.models.objectconnection import ObjectConnection
from noc.maintenance.models.maintenance import Maintenance
from noc.core.geo import get_bbox
from noc.config import config


class AlarmHeatCard(BaseCard):
    name = "alarmheat"
    card_css = ["/ui/pkg/leaflet/leaflet.css", "/ui/card/css/alarmheat.css"]

    default_template_name = "alarmheat"

    _layer_cache = {}
    TOOLTIP_LIMIT = config.card.alarmheat_tooltip_limit

    @property
    def card_js(self) -> List[str]:
        res = [
            "/ui/pkg/leaflet/leaflet.js",
            "/ui/pkg/leaflet.heat/leaflet-heat.js",
        ]

        if config.gis.yandex_supported:
            res += [
                "/ui/pkg/leaflet/yapi.js",
                "/ui/pkg/leaflet/Yandex.js",
            ]

        res += [
            "/ui/common/map_layer_creator.js",
            "/ui/common/settings_loader.js",
            "/ui/card/js/alarmheat.js",
        ]

        return res

    def get_data(self):
        return {
            "maintenance": 0,
            "lon": self.current_user.heatmap_lon or 0,
            "lat": self.current_user.heatmap_lat or 0,
            "zoom": self.current_user.heatmap_zoom or 0,
        }

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_layer_cache"))
    def get_pop_layers(cls):
        return list(Layer.objects.filter(code__startswith="pop_"))

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
        active_layers = [
            l_r for l_r in self.get_pop_layers() if l_r.min_zoom <= zoom <= l_r.max_zoom
        ]
        alarms: List[Dict[str, str]] = []
        res: Dict[int, Dict[str, Any]] = {}
        services: Dict[str, int] = {}
        subscribers: Dict[str, int] = {}
        t_data: Dict[Tuple[float, float] : List[Tuple[Dict[str, str], int]]] = defaultdict(list)
        mos = ManagedObject.objects.filter(is_managed=True).values("id", "name", "x", "y")
        if not self.current_user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(self.current_user))
        for mo in mos:
            res[mo["id"]] = mo
        if ms == 0:
            mos_id: List[int] = list(set(res.keys()) - set(Maintenance.currently_affected()))
        else:
            mos_id: List[int] = list(res.keys())
        for a in ActiveAlarm._get_collection().find(
            {"managed_object": {"$in": mos_id, "$exists": True}},
            {"_id": 1, "managed_object": 1, "direct_subscribers": 1, "direct_services": 1},
        ):
            s_sub, s_service = {}, {}
            if a.get("direct_subscribers"):
                s_sub = {dsub["profile"]: dsub["summary"] for dsub in a["direct_subscribers"]}
            if a.get("direct_services"):
                s_service = {dserv["profile"]: dserv["summary"] for dserv in a["direct_services"]}
            mo: Dict[str, Any] = res.get(a["managed_object"])
            if not mo:
                continue
            if mo["x"] and mo["y"]:
                w = ServiceSummary.get_weight({"subscriber": s_sub, "service": s_service})
                # @todo: Should we add the object's weight to summary?
                # @todo: Check west/south hemisphere
                if active_layers and west <= mo["x"] <= east and south <= mo["y"] <= north:
                    t_data[mo["x"], mo["y"]] += [(mo, w)]
            else:
                w = 0
            alarms += [
                {
                    "alarm_id": str(a.get("_id")),
                    "managed_object": mo["name"],
                    "x": mo["x"],
                    "y": mo["y"],
                    "w": max(w, 1),
                }
            ]
            if s_service:
                update_dict(services, s_service)
            if s_sub:
                update_dict(subscribers, s_sub)
        links = None
        o_seen = set()
        points = None
        o_data: Dict[Tuple[float, float], List[Dict[str, Any]]] = {}
        if t_data and active_layers:
            # Create lines
            bbox = get_bbox(west, east, north, south)
            lines = []
            for d in ObjectConnection._get_collection().find(
                {
                    "type": "pop_link",
                    "layer": {"$in": [a_l.id for a_l in active_layers]},
                    "line": {"$geoIntersects": {"$geometry": bbox}},
                },
                {"_id": 0, "connection": 1, "line": 1},
            ):
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
                data: Dict[int, int] = {}
                for mo, w in o_data[x, y]:
                    if mo["id"] not in data:
                        data[mo["id"]] = w
                data: List[int] = sorted(data, key=lambda z: data[z], reverse=True)[
                    : self.TOOLTIP_LIMIT
                ]
                points += [
                    geojson.Feature(
                        geometry=geojson.Point(coordinates=(x, y)),
                        properties={
                            "alarms": len(t_data[x, y]),
                            "objects": [
                                {
                                    "id": res[mo_id]["id"],
                                    "name": res[mo_id]["name"],
                                    "address": res[mo_id].get("address"),
                                }
                                for mo_id in data
                            ],
                        },
                    )
                ]
            points = geojson.FeatureCollection(features=points)
        return {
            "alarms": alarms,
            "summary": self.f_glyph_summary({"service": services, "subscriber": subscribers}),
            "links": links,
            "pops": points,
        }
