# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MonMap
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import itertools
from collections import defaultdict
# Third-party modules
import cachetools
from mongoengine import ValidationError
# import geojson
# import random
# NOC modules
from noc.services.card.cards.base import BaseCard
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import ServiceSummary
from noc.gis.models.layer import Layer
from noc.config import config


class MonMapCard(BaseCard):
    name = "monmap"
    card_css = [
        "/ui/pkg/leaflet/leaflet.css",
        "/ui/pkg/leaflet.markercluster/MarkerCluster.css",
        "/ui/card/css/monmap.css"
    ]
    card_js = [
        "/ui/pkg/leaflet/leaflet.js",
        "/ui/pkg/leaflet.heat/leaflet-heat.js",
        "/ui/pkg/leaflet.markercluster/leaflet.markercluster.js",
        "/ui/card/js/monmap.js"
    ]

    default_template_name = "monmap"
    o_default_name = "Root"

    color_map = {"error": "#FF0000",
                 "warning": "#F0C20C",
                 "good": "#6ECC39",
                 "default": "#6ECC39"}

    _layer_cache = {}
    TOOLTIP_LIMIT = config.card.alarmheat_tooltip_limit

    def get_object(self, id=None):
        if id:
            self.root = Object.get_by_id(id=id)
        else:
            self.root = Object.objects.get(name=self.o_default_name)

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

        object_id = self.handler.get_argument("object_id")
        # zoom = int(self.handler.get_argument("z"))
        # west = float(self.handler.get_argument("w"))
        # east = float(self.handler.get_argument("e"))
        # north = float(self.handler.get_argument("n"))
        # south = float(self.handler.get_argument("s"))
        # ms = int(self.handler.get_argument("maintenance"))
        # active_layers = [l for l in self.get_pop_layers() if l.min_zoom <= zoom <= l.max_zoom]
        if self.current_user.is_superuser:
            moss = ManagedObject.objects.filter(is_managed=True)
        else:
            moss = ManagedObject.objects.filter(is_managed=True,
                                                administrative_domain__in=self.get_user_domains())
        objects = []
        sss = {"error": {},
               "warning": {},
               "good": {}}
        s_def = {
            "service": {},
            "subscriber": {},
            "interface": {}
        }
        services = defaultdict(list)
        try:
            object_root = Object.objects.filter(id=object_id).first()
        except ValidationError:
            object_root = None
        if object_root:
            con = self.get_containers_by_root(object_root.id)
            moss = moss.filter(container__in=con).exclude(container=None).order_by("container")
        else:
            moss = moss.exclude(container=None).order_by("container")

        # Getting Alarms severity dict MO: Severity @todo List alarms
        alarms = {aa["managed_object"]: aa["severity"] for aa in ActiveAlarm.objects.filter(
            managed_object__in=list(moss.values_list("id", flat=True))
        ).scalar("managed_object", "severity").as_pymongo()}
        # Getting services
        s_services = ServiceSummary.get_objects_summary(list(moss.values_list("id", flat=True)))
        # Getting containers name and coordinates
        containers = {str(o["_id"]): (o["name"], o["data"]) for o in Object.objects.filter(
            data__geopoint__exists=True).fields(id=1, name=1, data__geopoint__x=1,
                                                data__geopoint__y=1).as_pymongo()}
        # Main Loop. Get ManagedObject group by container
        for container, mol in itertools.groupby(moss.values_list("id", "name", "container"), key=lambda o: o[2]):
            name, data = containers.get(container, ("", {"geopoint": {}}))
            x = data["geopoint"].get("x")
            y = data["geopoint"].get("y")
            if not x or not y:
                continue
            ss = {"objects": [],
                  "total": 0,
                  "error": 0,
                  "warning": 0,
                  "good": 0
                  }
            for mo_id, mo_name, container in mol:
                # Status by alarm severity
                s_service = s_services.get(mo_id, s_def)
                status = "good"
                if 100 < alarms.get(mo_id) < 2000:
                    status = "warning"
                elif alarms.get(mo_id) > 2000:
                    status = "error"
                update_dict(sss[status], s_service["service"])
                ss[status] += 1
                ss["total"] += 1
                ss["objects"] += [{"id": mo_id, "name": mo_name, "status": status}]
            objects += [{
                "name": name,
                "id": str(container),
                "x": x,
                "y": y,
                "objects": [],
                "total": 0,
                "error": 0,
                "warning": 0,
                "good": 0}]
            objects[-1].update(ss)

        for r in ["error", "warning", "good"]:
            for p in sss[r]:
                services[p] += [(self.color_map.get(r, self.color_map["default"]),
                                 sss[r].get(p, 0))]
        return {
            "objects": objects,
            "summary": self.f_glyph_summary({
                "service": services
                # "subscriber": subscribers
            }),
        }

    @staticmethod
    def get_containers_by_root(root_id=None):
        """
        Getting all containers from root object
        # @todo containers only with coordinates (Filter by models)
        # @todo containers only
        # from noc.sa.models.managedobject import ManagedObject
        # from noc.inv.models.object import Object
        # If None - all objects
        """
        root = Object.get_by_id(root_id)
        work_set = {root.id}
        os = set()
        kk = None
        for r in range(1, 9):
            work_set = set(Object.objects.filter(container__in=list(work_set)).values_list("id"))
            # work_set |= work_set.union(os)
            os |= work_set
            if len(work_set) == kk:
                break
            kk = len(work_set)
            # print len(work_set)
            # print len(os)
        return os

    def f_glyph_summary(self, s, collapse=False):
        def get_summary(d, profile):
            v = []
            if hasattr(profile, "show_in_summary"):
                def show_in_summary(p):
                    return p.show_in_summary
            else:
                def show_in_summary(p):
                    return True
            # for p, c in sorted(d.items(), key=lambda x: -x[1]):
            for p, c in sorted(d.items()):
                pv = profile.get_by_id(p)
                if pv and show_in_summary(pv):
                    if isinstance(c, list):
                        badge = "".join(" <span class=\"badge\" style=\"color: %s\">%s</span>" % cc for cc in c)
                        badge += "</div>"
                    else:
                        if collapse and c < 2:
                            badge = "</div>"
                        else:
                            badge = "<span class=\"badge\">%s</span></div>" % c
                    v += [
                        "<div style='float: left;clear: left;'><i style='width: 50px;' class=\"%s\" title=\"%s\"></i>%s" % (
                            pv.glyph,
                            pv.name,
                            badge
                        )
                    ]
            return " ".join(v)

        if not isinstance(s, dict):
            return ""
        r = []
        if "subscriber" in s:
            from noc.crm.models.subscriberprofile import SubscriberProfile
            r += [get_summary(s["subscriber"], SubscriberProfile)]
        if "service" in s:
            from noc.sa.models.serviceprofile import ServiceProfile
            r += [get_summary(s["service"], ServiceProfile)]
        if "fresh_alarms" in s and s["fresh_alarms"]:
            r += ["<i class=\"fa fa-exclamation-triangle\"></i><span class=\"badge\">%s</span>"
                  % s["fresh_alarms"]["FreshAlarm"]]
        r = [x for x in r if x]
        return "&nbsp;".join(r)
