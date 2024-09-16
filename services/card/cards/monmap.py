# ---------------------------------------------------------------------
# MonMap
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import itertools
from collections import defaultdict
from typing import List

# Third-party modules
import cachetools
from mongoengine import ValidationError
from pymongo import ReadPreference

# import geojson
# import random
# NOC modules
from .base import BaseCard
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject
from noc.maintenance.models.maintenance import Maintenance
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import ServiceSummary
from noc.gis.models.layer import Layer
from noc.config import config


class MonMapCard(BaseCard):
    name = "monmap"
    card_css = [
        "/ui/pkg/leaflet/leaflet.css",
        "/ui/pkg/leaflet.markercluster/MarkerCluster.css",
        "/ui/card/css/monmap.css",
    ]

    default_template_name = "monmap"
    o_default_name = "Root"

    color_map = {
        "error": "#FF0000",
        "warning": "#F0C20C",
        "good": "#6ECC39",
        "maintenance": "#2032A0",
        "default": "#6ECC39",
    }

    fake_service = "5a9f7309c165cf528d9d8f95"

    _layer_cache = {}
    TOOLTIP_LIMIT = config.card.alarmheat_tooltip_limit

    @property
    def card_js(self) -> List[str]:
        res = [
            "/ui/pkg/leaflet/leaflet.js",
            "/ui/pkg/leaflet.heat/leaflet-heat.js",
            "/ui/pkg/leaflet.markercluster/leaflet.markercluster.js",
            "/ui/pkg/leaflet.featuregroup.subgroup/leaflet.featuregroup.subgroup.js",
        ]

        if config.gis.yandex_supported:
            res += [
                "/ui/pkg/leaflet/yapi.js",
                "/ui/pkg/leaflet/Yandex.js",
            ]

        res += [
            "/ui/common/map_layer_creator.js",
            "/ui/common/settings_loader.js",
            "/ui/card/js/monmap.js",
        ]

        return res

    def get_object(self, id=None):
        if id:
            self.root = Object.get_by_id(id=id)
        else:
            self.root = Object.objects.get(name=self.o_default_name)

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
        object_id = self.handler.get_argument("object_id")
        if self.current_user.is_superuser:
            moss = ManagedObject.objects.filter(is_managed=True)
        else:
            moss = ManagedObject.objects.filter(
                is_managed=True, administrative_domain__in=self.get_user_domains()
            )
        objects = []
        objects_status = {"error": [], "warning": [], "good": [], "maintenance": []}
        sss = {"error": {}, "warning": {}, "good": {}, "maintenance": {}}
        services = defaultdict(list)
        try:
            object_root = Object.objects.filter(id=object_id).first()
        except ValidationError:
            object_root = None
        if object_root:
            con = [str(c) for c in self.get_containers_by_root(object_root.id)]
            moss = moss.filter(container__in=con).order_by("container")
        else:
            moss = moss.exclude(container=None).order_by("container")
            con = list(moss.values_list("container", flat=True))
        mo_ids = list(moss.values_list("id", flat=True))
        # Getting Alarms severity dict MO: Severity @todo List alarms
        if not object_root:
            alarms = self.get_alarms_info(None, alarms_all=True)
        else:
            alarms = self.get_alarms_info(mo_ids)
        # Get maintenance
        maintenance = Maintenance.currently_affected()
        # Getting services
        if not object_root:
            services_map = self.get_objects_summary_met(mo_ids, info_all=True)
        else:
            services_map = self.get_objects_summary_met(mo_ids)
        # Getting containers name and coordinates
        containers = {
            str(o["_id"]): (
                o["name"],
                {
                    "%s.%s" % (item["interface"], item["attr"]): item["value"]
                    for item in o.get("data", [])
                },
            )
            for o in Object.objects.filter(data__match={"interface": "geopoint"}, id__in=con)
            .read_preference(ReadPreference.SECONDARY_PREFERRED)
            .fields(id=1, name=1, data=1)
            .as_pymongo()
        }
        # Main Loop. Get ManagedObject group by container
        for container, mol in itertools.groupby(
            moss.values_list("id", "name", "container").order_by("container"), key=lambda o: o[2]
        ):
            name, data = containers.get(container, ("", {"geopoint": {}}))
            x = data.get("geopoint.x")
            y = data.get("geopoint.y")
            address = data.get("address.text", "")
            ss = {"objects": [], "total": 0, "error": 0, "warning": 0, "good": 0, "maintenance": 0}
            for mo_id, mo_name, container in mol:
                # Status by alarm severity
                # s_service = s_services.get(mo_id, s_def)
                status = "good"
                if mo_id in maintenance:
                    status = "maintenance"
                elif 100 < alarms.get(mo_id, 0) <= 2000:
                    status = "warning"
                elif alarms.get(mo_id, 0) > 2000:
                    status = "error"
                objects_status[status] += [mo_id]
                ss[status] += 1
                ss["total"] += 1
                services_ss = [
                    "%s-%s" % (sm, status) for sm in services_map.get(mo_id, [self.fake_service])
                ]
                ss["objects"] += [
                    {"id": mo_id, "name": mo_name, "status": status, "services": services_ss}
                ]
            if not x or not y:
                continue
            objects += [
                {
                    "name": address or name,
                    "id": str(container),
                    "x": x if x > -168 else x + 360,  # For Chukotskiy AO
                    "y": y,
                    "objects": [],
                    "total": 0,
                    "error": 0,
                    "warning": 0,
                    "good": 0,
                    "maintenance": 0,
                }
            ]
            objects[-1].update(ss)

        profiles = set()
        for r in ["error", "warning", "good", "maintenance"]:
            if not objects_status[r]:
                continue
            if not object_root and r == "good":
                m_services, m_subscribers = ServiceSummary.get_direct_summary(
                    objects_status[r], summary_all=True
                )
            else:
                m_services, m_subscribers = ServiceSummary.get_direct_summary(objects_status[r])
            profiles |= set(m_services)
            sss[r] = m_services
        for r in sorted(sss, key=lambda k: ("error", "warning", "good", "maintenance").index(k)):
            for p in profiles:
                services[p] += [(r, sss[r].get(p, None))]
        return {
            "objects": objects,
            "summary": self.f_glyph_summary({"service": services}),
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
        coll = Object._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        )
        work_set = {root.id}
        os = set()
        kk = None
        for r in range(1, 9):
            work_set = set(
                o["_id"] for o in coll.find({"container": {"$in": list(work_set)}}, {"_id": 1})
            )
            # work_set |= work_set.union(os)
            os |= work_set
            if len(work_set) == kk:
                break
            kk = len(work_set)
        return os

    @staticmethod
    def get_alarms_info(mo_ids, alarms_all=False):
        q = {"severity": {"$exists": True}}
        if not alarms_all:
            q["managed_object"] = {"$in": mo_ids}
        coll = ActiveAlarm._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        )
        r = {}
        for o in coll.find(q, {"managed_object": 1, "severity": 1, "_id": 0}):
            if (
                o["managed_object"] in r and r[o["managed_object"]] > o["severity"]
            ):  # Save alarm with max severity
                continue
            r[o["managed_object"]] = o["severity"]
        return r

    def f_glyph_summary(self, s, collapse=False):
        def get_summary(d, profile):
            # d - {profile_id1: [(color1, sum1), (color2, sum2), ...], profile_id2: [ ... ]}
            v = ["<table>", "<tbody style='text-align: right;'>"]
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
                        badge = []
                        for color, count in c:
                            if count is None:
                                badge += ["<td style='padding-right: 15px;'>&nbsp;</td>"]
                            else:
                                html1 = "".join(
                                    [
                                        "<td style='padding-right: ",
                                        "15px;'><span class='badge' ",
                                        "style='color: %s;cursor: pointer;'",
                                        " id='%s-%s'>%s</span></td>",
                                    ]
                                )
                                badge += [
                                    html1
                                    % (  # noqa
                                        self.color_map.get(color, self.color_map["default"]),
                                        pv.id,
                                        color,
                                        count,
                                    )
                                ]
                        badge = "".join(badge)
                    elif collapse and c < 2:
                        badge = "</div>"
                    else:
                        badge = '<span class="badge">%s</span></div>' % c
                    html2 = "".join(
                        [
                            "<td style='text-align: center; width: ",
                            "50px; padding-right: 15px;'><i class='%s'",
                            " title='%s' style='cursor: pointer;' id='%s'></i></td>",
                        ]
                    )
                    v += ["<tr>", html2 % (pv.glyph, pv.name, pv.id), badge, "<tr/>"]

            v += ["</tbody>", "</table>"]
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
            r += [
                '<i class="fa fa-exclamation-triangle"></i><span class="badge">%s</span>'
                % s["fresh_alarms"]["FreshAlarm"]
            ]
        r = [x for x in r if x]
        return "&nbsp;".join(r)

    @staticmethod
    def get_objects_summary_met(mos_ids, info_all=False):
        kk = {}
        pipeline = []
        name = "service"
        if not info_all:
            pipeline += [{"$match": {"managed_object": {"$in": mos_ids}}}]

        group = {"_id": {"mo": "$managed_object"}, "count": {"$push": "$%s.profile" % name}}
        pipeline += [{"$unwind": "$%s" % name}, {"$group": group}]
        for ss in (
            ServiceSummary._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(pipeline)
        ):
            kk[ss["_id"]["mo"]] = ss["count"]
        return kk
