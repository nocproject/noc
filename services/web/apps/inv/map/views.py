# ---------------------------------------------------------------------
# inv.map application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import itertools
import threading
from collections import defaultdict
from typing import List, Set, Dict, Any

# Third-party modules
from concurrent.futures import ThreadPoolExecutor, as_completed
from jinja2.environment import Environment
from jinja2.exceptions import TemplateError
from bson import ObjectId

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.interface import Interface
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.mapsettings import MapSettings
from noc.inv.models.link import Link
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.cpe import CPE
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.base import (
    ListOfParameter,
    IntParameter,
    StringParameter,
    DictListParameter,
    DictParameter,
)
from noc.fm.models.activealarm import ActiveAlarm
from noc.maintenance.models.maintenance import Maintenance
from noc.core.text import alnum_key
from noc.core.validators import is_objectid
from noc.core.pm.utils import get_interface_metrics, MetricProxy
from noc.core.translation import ugettext as _
from noc.core.cache.decorator import cachedmethod
from noc.core.topology.loader import loader

tags_lock = threading.RLock()


class MapApplication(ExtApplication):
    """
    inv.net application
    """

    title = _("Network Map")
    menu = _("Network Map")
    glyph = "globe"

    implied_permissions = {"launch": ["inv:networksegment:lookup"]}
    lookup_default = [{"id": "Leave unchanged", "label": "Leave unchanged"}]
    gen_param = "generator"
    gen_id_param = "generator_id"
    q_parent = "parent"

    # Object statuses
    ST_UNKNOWN = 0  # Object state is unknown
    ST_OK = 1  # Object is OK
    ST_ALARM = 2  # Object is reachable, Active alarms
    ST_UNREACH = 3  # Object is unreachable due to other's object failure
    ST_DOWN = 4  # Object is down
    ST_MAINTENANCE = 32  # Maintenance bit

    @view(
        r"^(?P<gen_type>\w+)/(?P<gen_id>[0-9a-f]{24}|\d+)/data/$",
        method=["GET"],
        access="read",
        api=True,
    )
    def api_data(self, request, gen_type, gen_id):
        """
        Return data for render map
        :param request:
        :param gen_type:
        :param gen_id:
        :return:
        """
        try:
            return MapSettings.get_map(
                gen_type=gen_type, gen_id=gen_id, force_spring=request.GET.get("force") == "spring"
            )
        except ValueError as e:
            return {"id": gen_id, "name": f"{gen_type}: {gen_id}", "error": str(e)}

    @view(
        r"^(?P<gen_type>\w+)/(?P<gen_id>[0-9a-f]{24}|\d+)/data/$",
        method=["POST"],
        access="write",
        api=True,
    )
    def api_save(self, request, gen_type, gen_id):
        """
        Save Manual layout
        :param request:
        :param gen_type:
        :param gen_id:
        :return:
        """
        data = self.deserialize(request.body)
        data["id"] = gen_id
        data["gen_type"] = gen_type
        MapSettings.load_json(data, request.user.username)
        return {"status": True}

    @view(
        r"^(?P<gen_type>\w+)/(?P<gen_id>[0-9a-f]{24}|\d+)/data/$",
        method=["DELETE"],
        access="write",
        api=True,
    )
    def api_reset(self, request, gen_type, gen_id):
        # MapSettings.objects.filter(gen_type=gen_type, gen_id=gen_id).delete()
        settings = MapSettings.objects.filter(gen_type=gen_type, gen_id=gen_id).first()
        if settings:
            settings.nodes = []
            settings.links = []
            settings.save()
        return {"status": True}

    # Inspectors

    def inspector_managedobject(self, request, id, mo_id):
        # segment = self.get_object_or_404(NetworkSegment, id=id)
        if is_objectid(id):
            segment = NetworkSegment.get_by_id(str(id))
        else:
            mo = ManagedObject.get_by_id(id)
            if mo:
                segment = mo.segment
        object = self.get_object_or_404(ManagedObject, id=int(mo_id))
        s = {1: "telnet", 2: "ssh", 3: "http", 4: "https", 5: "beef"}[object.scheme]
        r = {
            "id": object.id,
            "name": object.name,
            "description": object.description,
            "address": object.address,
            "platform": object.platform.full_name if object.platform else "",
            "profile": object.profile.name,
            "external": segment and object.segment.id != segment.id,
            "external_segment": {"id": str(object.segment.id), "name": object.segment.name},
            # "external": object.segment.id != segment.id,
            # "external_segment": {"id": str(object.segment.id), "name": object.segment.name},
            "caps": object.get_caps(),
            "console_url": "%s://%s/" % (s, object.address),
        }
        return r

    def inspector_objectgroup(self, request, id, rg_id):
        object = self.get_object_or_404(ResourceGroup, id=rg_id)
        return {
            "id": str(object.id),
            "name": object.name,
            "description": object.description,
            "external": False,
            "external_segment": {},
        }

    def inspector_objectsegment(self, request, id, rg_id):
        object = self.get_object_or_404(NetworkSegment, id=rg_id)
        return {
            "id": str(object.id),
            "name": object.name,
            "description": object.description,
            "external": False,
            "external_segment": {},
        }

    def inspector_link(self, request, id, link_id):
        """
        Link inpector
        :param request:
        :param id:
        :param link_id:
        :return:
        """
        link = self.get_object_or_404(Link, id=link_id)
        r = {
            "id": str(link.id),
            "name": link.name or None,
            "description": link.description or None,
            "objects": [],
            "method": link.discovery_method,
        }
        o = defaultdict(list)
        for i in link.interfaces:
            o[i.managed_object] += [i]
        for mo in sorted(o, key=lambda x: x.name):
            r["objects"] += [
                {
                    "id": mo.id,
                    "name": mo.name,
                    "interfaces": [
                        {"name": i.name, "description": i.description or None, "status": i.status}
                        for i in sorted(o[mo], key=lambda x: alnum_key(x.name))
                    ],
                }
            ]
        # Get link bandwidth
        mo_in = defaultdict(float)
        mo_out = defaultdict(float)
        mos = [ManagedObject.get_by_id(mo["id"]) for mo in r["objects"]]
        metric_map, last_ts = get_interface_metrics(list(o))
        for mo in o:
            if mo not in metric_map:
                continue
            for i in o[mo]:
                if i.name not in metric_map[mo]:
                    continue
                mo_in[mo] += int(metric_map[mo][i.name]["load_in"])
                mo_out[mo] += int(metric_map[mo][i.name]["load_out"])
        if len(mos) == 2:
            mo1, mo2 = mos
            r["utilisation"] = [
                int(max(mo_in[mo1], mo_out[mo2])),
                int(max(mo_in[mo2], mo_out[mo1])),
            ]
        else:
            mv = list(mo_in.values()) + list(mo_out.values())
            if mv:
                r["utilisation"] = [int(max(mv))]
            else:
                r["utilisation"] = 0
        return r

    def inspector_cloud(self, request, id, link_id):
        self.get_object_or_404(NetworkSegment, id=id)
        link = self.get_object_or_404(Link, id=link_id)
        r = {
            "id": str(link.id),
            "name": link.name or None,
            "description": link.description or None,
            "objects": [],
            "method": link.discovery_method,
        }
        o = defaultdict(list)
        for i in link.interfaces:
            o[i.managed_object] += [i]
        for mo in sorted(o, key=lambda x: x.name):
            r["objects"] += [
                {
                    "id": mo.id,
                    "name": mo.name,
                    "interfaces": [
                        {"name": i.name, "description": i.description or None, "status": i.status}
                        for i in sorted(o[mo], key=lambda x: alnum_key(x.name))
                    ],
                }
            ]
        return r

    def inspector_cpe(self, request, id, cpe_id):
        cpe: "CPE" = self.get_object_or_404(CPE, id=cpe_id)
        caps = cpe.get_caps()
        r = {
            "id": str(cpe.id),
            "name": str(cpe),
            "description": cpe.description,
            "address": cpe.address,
            "platform": caps.get("CPE | Model"),
            # "external": object.segment.id != segment.id,
            # "external_segment": {"id": str(object.segment.id), "name": object.segment.name},
            "caps": caps,
        }
        return r

    @view(
        url=r"^info/(?P<inspector>\w+)/(?P<gen_id>[0-9a-f]{24}|\d+)/(?P<r_id>([0-9a-f]{24}|\d+))/$",
        method=["GET"],
        access="read",
        api=True,
    )
    def inspector(self, request, inspector, gen_id, r_id):
        """
        API for map inspectors
        :param request:
        :param inspector: Inspector name (node type)
        :param gen_id: Generator Id
        :param r_id: node_id
        :return:
        """
        if not hasattr(self, f"inspector_{inspector}"):
            self.logger.warning("Unknown inspector: %s", inspector)
            return
        hi = getattr(self, f"inspector_{inspector}")
        return hi(request, gen_id, r_id)

    @view(url=r"^info/segment/(?P<id>[0-9a-f]{24})/$", method=["GET"], access="read", api=True)
    def api_info_segment(self, request, id):
        segment = self.get_object_or_404(NetworkSegment, id=id)
        r = {
            "name": segment.name,
            "description": segment.description,
            "objects": segment.managed_objects.count(),
        }
        return r

    @view(method=["GET"], url=r"^lookup/$", access="lookup", api=True)
    def api_lookup(self, request):
        """
        Lookup available map by generator.
        """

        def get_root() -> list[dict[str, Any]]:
            """Render root node."""
            r = []
            for mi in loader:
                mi = loader[mi]
                if mi.is_empty():
                    continue
                r.append(
                    {
                        "id": mi.name,
                        "generator": mi.name,
                        "label": mi.header or mi.name,
                        "has_children": True,
                        "only_container": True,
                    }
                )
            return r

        # Get parent
        g = request.GET
        parent = g.get("parent") or ""
        # Render parent?
        if not parent:
            return get_root()
        # Check generator
        generator_name = g.get(self.gen_param) or ""
        gen = loader[generator_name]
        if not gen:
            return self.render_json(
                {"success": False, "message": f"Unknown generator: {generator_name}"},
                status=self.NOT_FOUND,
            )
        # Search for maps
        r = []
        for mi in gen.iter_maps(
            parent=parent if gen.name != parent else None,
            query=g.get(self.query_param, ""),
            limit=int(g.get(self.limit_param, 500)),
            start=int(g.get(self.start_param, 0)),
            page=int(g.get(self.page_param, 1)),
        ):
            r.append(
                {
                    "label": mi.title,
                    "generator": mi.generator,
                    "id": str(mi.id),
                    "has_children": mi.has_children,
                    "only_container": mi.only_container,
                    "code": mi.code,
                }
            )
        return r

    @view(
        method=["GET"], url=r"^(?P<gen_id>[0-9a-f]{24}|\d+)/get_path/$", access="lookup", api=True
    )
    def api_lookup_maps_get_path(self, request, gen_id):
        """

        :param request:
        :param gen_id:
        :return:
        """
        # Parse params
        q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
        if self.gen_param not in q:
            return self.response_bad_request(f"Required {self.gen_param} param on request")
        gen = loader[q[self.gen_param]]
        if not gen:
            return self.render_json(
                {"success": False, "message": f"Unknown generator: {q[self.gen_param]}"},
                status=self.NOT_FOUND,
            )
        return {
            "data": [{"level": 0, "id": 0, "generator": gen.name, "label": gen.header}]
            + [
                {"level": p.level, "id": str(p.id), "generator": gen.name, "label": p.title}
                for p in gen.iter_path(gen_id)
            ]
        }

    @view(
        url=r"^objects_statuses/$",
        method=["POST"],
        access="read",
        api=True,
        validate={
            "nodes": DictListParameter(
                attrs={
                    "id": StringParameter(),
                    "node_type": StringParameter(),
                    "node_id": StringParameter(),
                    "metrics_template": StringParameter(required=False),
                    "object_filter": StringParameter(required=False),
                }
            )
        },
    )
    def api_objects_statuses(self, request, nodes: List[Dict[str, str]]):
        def get_alarms(objects: List[int]) -> Set[int]:
            """
            Returns a set of objects with alarms
            """
            alarms: Set[int] = set()
            coll = ActiveAlarm._get_collection()
            while objects:
                chunk, objects = objects[:500], objects[500:]
                a = coll.aggregate(
                    [
                        {"$match": {"managed_object": {"$in": chunk}}},
                        {"$group": {"_id": "$managed_object", "count": {"$sum": 1}}},
                    ]
                )
                alarms.update(d["_id"] for d in a)
            return alarms

        def get_alarms_segment(segments: List[str]) -> Set[str]:
            if not segments:
                return set()
            coll = ActiveAlarm._get_collection()
            return {
                str(sa["_id"])
                for sa in coll.aggregate(
                    [
                        {"$match": {"segment_path": {"$in": [ObjectId(ss) for ss in segments]}}},
                        {"$unwind": "$segment_path"},
                        {"$group": {"_id": "$segment_path", "count": {"$sum": 1}}},
                    ]
                )
            }

        nid = {}
        metrics_template: Dict[str, str] = {}
        group_nodes = {}  # (segment, group)
        cpes = set()
        # Build id -> object_id mapping
        for o in nodes:
            if o["node_type"] == "managedobject":
                nid[o["node_id"]] = o["id"]
                metrics_template[o["id"]] = o["metrics_template"]
            elif o["node_type"] == "objectgroup":
                group_nodes[("", o["node_id"])] = o["id"]
            elif o["node_type"] == "objectsegment":
                group_nodes[(o["node_id"], "")] = o["id"]
            elif o["node_type"] == "cpe":
                cpes.add(o["node_id"])
                metrics_template[o["id"]] = o["metrics_template"]
            elif o["node_type"] == "other" and o.get("object_filter"):
                group_nodes[
                    (
                        o["object_filter"].get("segment", ""),
                        o["object_filter"].get("resource_group", ""),
                    )
                ] = o["id"]
        object_group = defaultdict(set)  # mo_id -> groups
        # Processed groups
        for (segment, group), n_id in group_nodes.items():
            if not group:
                continue
            if not segment:
                mos = ManagedObject.objects.filter(
                    effective_service_groups__overlap=[group]
                ).values_list("id", flat=True)
            else:
                mos = ManagedObject.objects.filter(
                    effective_service_groups__overlap=[group], segment=segment
                ).values_list("id", flat=True)
            for mo_id in mos:
                object_group[mo_id].add(n_id)
        # Mark all as unknown
        objects = [int(x) for x in itertools.chain(nid, object_group)]
        bi_id_map = {
            str(mo_id): bi_id
            for mo_id, bi_id in ManagedObject.objects.filter(id__in=objects).values_list(
                "id", "bi_id"
            )
        }
        env = Environment()
        env.globals["metric"] = MetricProxy(
            metric_keys=[{"managed_object": bi_id} for bi_id in bi_id_map.values()]
        )
        r = defaultdict(dict)
        for o in itertools.chain(nid.values(), group_nodes.values()):
            r[o]["status_code"] = self.ST_UNKNOWN
            if o not in metrics_template:
                continue
            try:
                r[o]["metrics_label"] = env.from_string(metrics_template[o]).render(
                    {"managed_object": bi_id_map[o]}
                )
            except (ValueError, TemplateError) as e:
                r[o]["metrics_label"] = "#ERROR#"
                self.logger.error(
                    "[%s] Error when processed MetricTemplate: %s", metrics_template[o], e
                )
        sr = ManagedObject.get_statuses(objects)
        sa = get_alarms(objects)
        mo = Maintenance.currently_affected(objects)
        # Nodes Status
        group_status = defaultdict(set)
        for o in sr:
            if sr[o]:
                # Check for alarms
                if o in sa:
                    r[str(o)]["status_code"] = self.ST_ALARM
                else:
                    r[str(o)]["status_code"] = self.ST_OK
            else:
                r[str(o)]["status_code"] = self.ST_DOWN
            if o in mo:
                r[str(o)]["status_code"] |= self.ST_MAINTENANCE
            if o not in object_group:
                continue
            for g in object_group[o]:
                group_status[g].add(r[o]["status_code"])
        for g, status in group_status.items():
            if self.ST_ALARM in status or self.ST_DOWN in status:
                r[str(o)]["status_code"] = self.ST_ALARM
            elif self.ST_OK in status:
                r[str(o)]["status_code"] = self.ST_OK
        segments = [s for s, g in group_nodes if not g]
        sa = get_alarms_segment(segments)
        for s in segments:
            if s in sa:
                r[str(o)]["status_code"] = self.ST_ALARM
            else:
                r[str(o)]["status_code"] = self.ST_OK
        if not cpes:
            return r
        # CPE
        cpe_map = {}
        for cpe in CPE.objects.filter(id__in=list(cpes)):
            o = str(cpe.id)
            cpe_map[cpe.bi_id] = o
            if cpe.oper_status is None:
                r[o]["status_code"] = self.ST_UNKNOWN
            elif not cpe.oper_status:
                r[o]["status_code"] = self.ST_ALARM
            else:
                r[o]["status_code"] = self.ST_OK
        env = Environment()
        env.globals["metric"] = MetricProxy(metric_keys=[{"cpe": x} for x in cpe_map])
        for cpe_bi_id, cpe_id in cpe_map.items():
            if cpe_id not in metrics_template:
                continue
            try:
                r[cpe_id]["metrics_label"] = env.from_string(metrics_template[cpe_id]).render(
                    {"cpe": cpe_bi_id}
                )
            except (ValueError, TemplateError) as e:
                r[cpe_id]["metrics_label"] = "#ERROR#"
                self.logger.error(
                    "[%s] Error when processed MetricTemplate: %s", metrics_template[cpe_id], e
                )
        return r

    @classmethod
    @cachedmethod(key="managedobject-name-to-id-%s", lock=lambda _: tags_lock)
    def managedobject_name_to_id(cls, name):
        r = ManagedObject.objects.filter(name=name).values_list("id")
        if r:
            return r[0][0]
        return None

    @classmethod
    @cachedmethod(key="interface-tags-to-id-%s-%s", lock=lambda _: tags_lock)
    def interface_tags_to_id(cls, object_name, interface_name):
        mo = cls.managedobject_name_to_id(object_name)
        i = Interface._get_collection().find_one({"managed_object": mo, "name": interface_name})
        if i:
            return i["_id"]
        return None

    @view(
        url=r"^metrics/$",
        method=["POST"],
        access="read",
        api=True,
        validate={
            "metrics": DictListParameter(
                attrs={
                    "id": StringParameter(),
                    "metric": StringParameter(),
                    "tags": DictParameter(),
                }
            )
        },
    )
    def api_metrics(self, request, metrics):
        def q(s):
            if isinstance(s, str):
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
                        self.interface_tags_to_id(m["tags"]["object"], m["tags"]["interface"])
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
            {"_id": {"$in": list(if_ids)}}, {"_id": 1, "admin_status": 1, "oper_status": 1}
        ):
            r[if_ids[d["_id"]]] = {
                "admin_status": d.get("admin_status", True),
                "oper_status": d.get("oper_status", True),
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
            r[pid]["Interface | Load | In"] = int(metric_map[rq_mo][rq_iface]["load_in"])
            r[pid]["Interface | Load | Out"] = int(metric_map[rq_mo][rq_iface]["load_out"])
        return r

    @view(
        url=r"^stp/status/$",
        method=["POST"],
        access="read",
        api=True,
        validate={"objects": ListOfParameter(IntParameter())},
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

        r = {"roots": [], "blocked": []}
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
