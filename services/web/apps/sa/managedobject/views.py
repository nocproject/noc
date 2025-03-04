# ---------------------------------------------------------------------
# sa.managedobject application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Tuple, List
from collections import defaultdict
import zlib

# Third-party modules
import orjson
import cachetools
from jinja2 import Template as Jinja2Template
from django.http import HttpResponse
from django.db.models import Q as d_Q
from mongoengine.queryset import Q as MQ

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.services.web.base.decorators.state import state_handler
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.managedobject import ManagedObject, ManagedObjectAttribute
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.interactionlog import InteractionLog
from noc.sa.models.profile import Profile
from noc.sa.models.cpestatus import CPEStatus
from noc.inv.models.capability import Capability
from noc.inv.models.link import Link
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.object import Object
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.services.web.base.modelinline import ModelInline
from noc.services.web.base.repoinline import RepoInline
from noc.project.models.project import Project
from noc.sa.interfaces.base import (
    ListOfParameter,
    ModelParameter,
    StringParameter,
    BooleanParameter,
    IntParameter,
    DictListParameter,
    DocumentParameter,
)
from noc.sa.models.action import Action
from noc.core.scheduler.job import Job
from noc.core.script.loader import loader as script_loader
from noc.core.mongo.connection import get_db
from noc.core.wf.interaction import Interaction
from noc.core.translation import ugettext as _
from noc.core.comp import smart_text, smart_bytes
from noc.core.geocoder.loader import loader as geocoder_loader
from noc.core.validators import is_objectid
from noc.core.debug import error_report
from noc.core.text import alnum_key
from noc.core.middleware.tls import get_user
from noc.core.pm.utils import get_interface_metrics
from noc.pm.models.scale import Scale
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.config import config

JP_CLAUSE_PATTERN = """jsonb_path_exists(caps, '$[*] ? (@.capability == "{}") ? (@.value {} {})')"""


@state_handler
class ManagedObjectApplication(ExtModelApplication):
    """
    ManagedObject application
    """

    title = _("Managed Objects")
    menu = _("Managed Objects")
    model = ManagedObject
    query_condition = "icontains"
    query_fields = ["name", "description"]
    secret_fields = {"password", "super_password", "snmp_ro", "snmp_rw"}
    ignored_fields = ExtModelApplication.ignored_fields | {"global_cpe_id", "local_cpe_id"}
    # Inlines
    attrs = ModelInline(ManagedObjectAttribute)
    cfg = RepoInline("config", access="config")

    extra_permissions = ["alarm", "change_interface", "commands"]
    implied_permissions = {"read": ["inv:networksegment:lookup", "main:handler:lookup"]}
    diverged_permissions = {"config": "read", "console": "script"}
    default_ordering = ["id"]
    order_map = {
        "link_count": " cardinality(links) ",
        "-link_count": " cardinality(links) ",
        "profile": "CASE %s END"
        % " ".join(
            [
                "WHEN %s='%s' THEN %s" % ("profile", pk, i)
                for i, pk in enumerate(Profile.objects.filter().order_by("name").values_list("id"))
            ]
        ),
        "-profile": "CASE %s END"
        % " ".join(
            [
                "WHEN %s='%s' THEN %s" % ("profile", pk, i)
                for i, pk in enumerate(Profile.objects.filter().order_by("-name").values_list("id"))
            ]
        ),
        "platform": "CASE %s END"
        % " ".join(
            [
                "WHEN %s='%s' THEN %s" % ("platform", pk, i)
                for i, pk in enumerate(Platform.objects.filter().order_by("name").values_list("id"))
            ]
        ),
        "-platform": "CASE %s END"
        % " ".join(
            [
                "WHEN %s='%s' THEN %s" % ("platform", pk, i)
                for i, pk in enumerate(
                    Platform.objects.filter().order_by("-name").values_list("id")
                )
            ]
        ),
        "version": "CASE %s END"
        % " ".join(
            [
                "WHEN %s='%s' THEN %s" % ("version", pk, i)
                for i, pk in enumerate(
                    Firmware.objects.filter().order_by("version").values_list("id")
                )
            ]
        ),
        "-version": "CASE %s END"
        % " ".join(
            [
                "WHEN %s='%s' THEN %s" % ("version", pk, i)
                for i, pk in enumerate(
                    Firmware.objects.filter().order_by("-version").values_list("id")
                )
            ]
        ),
    }
    resource_group_fields = [
        "static_service_groups",
        "effective_service_groups",
        "static_client_groups",
        "effective_client_groups",
    ]

    DISCOVERY_JOBS = [
        ("box", "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"),
        ("periodic", "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"),
    ]
    clean_fields = {"id": IntParameter(), "address": StringParameter(strip_value=True)}

    x_map = {
        "table_name": "interface",
        "map": {
            "load_in": "Interface | Load | In",
            "load_out": "Interface | Load | Out",
            "rx": "Interface | DOM | RxPower",
            "tx": "Interface | DOM | TxPower",
            "temp": "Interface | DOM | Temperature",
            "bias": "Interface | DOM | Bias Current",
        },
    }

    iface_metric_template = Jinja2Template(
        "In: {{load_in}}/Out: {{load_out}}/Rx: {{rx}}dBm/Tx: {{tx}}dBm/Temp:{{temp}}C/Bias: {{bias}}mA",
    )

    @staticmethod
    @cachetools.cached({})
    def get_ac_object_down():
        return AlarmClass.get_by_name("NOC | Managed Object | Ping Failed")

    def field_row_class(self, o):
        return o.object_profile.style.css_class_name if o.object_profile.style else ""

    def bulk_field_fav_status(self, data):
        user = get_user()
        fav_items = self.get_favorite_items(user)
        for r in data:
            r[self.fav_status] = r[self.pk] in fav_items
        return data

    def bulk_field_interface_count(self, data):
        """
        Apply interface_count fields
        :param data:
        :return:
        """
        mo_ids = [x["id"] for x in data]
        if not mo_ids:
            return data
        # Collect interface counts
        r = Interface._get_collection().aggregate(
            [
                {"$match": {"managed_object": {"$in": mo_ids}, "type": "physical"}},
                {"$group": {"_id": "$managed_object", "total": {"$sum": 1}}},
            ]
        )
        ifcount = {x["_id"]: x["total"] for x in r}
        # Apply interface counts
        for x in data:
            x["interface_count"] = ifcount.get(x["id"]) or 0
        return data

    def bulk_field_oper_state(self, data):
        """
        Apply oper_state field
        :param data:
        :return:
        """
        # IsManaged check if lookup field. Possibly extract if for id
        # Or Disable Bulk for lookup
        mo_ids = [x["id"] for x in data if x.get("is_managed") is not None]
        if not mo_ids:
            return data
        ac = self.get_ac_object_down()
        alarms = set(
            mo["managed_object"]
            for mo in ActiveAlarm._get_collection().find(
                {"alarm_class": {"$ne": ac.id}, "managed_object": {"$in": mo_ids}},
                {"managed_object": 1},
            )
        )
        # Apply oper_state
        for x in data:
            if "oper_state" not in x or x["oper_state"] in {"failed", "disabled"}:
                continue
            if x["id"] in alarms:
                x["oper_state"] = "degraded"
                x["oper_state__label"] = _("Warning")
        return data

    # def bulk_field_link_count(self, data):
    #     """
    #     Apply link_count fields
    #     :param data:
    #     :return:
    #     """
    #     mo_ids = [x["id"] for x in data]
    #     if not mo_ids:
    #         return data
    #     # Collect interface counts
    #     r = Link._get_collection().aggregate(
    #         [
    #             {"$match": {"linked_objects": {"$in": mo_ids}}},
    #             {"$unwind": "$linked_objects"},
    #             {"$group": {"_id": "$linked_objects", "total": {"$sum": 1}}},
    #         ]
    #     )
    #     links_count = {x["_id"]: x["total"] for x in r}
    #     # Apply interface counts
    #     for x in data:
    #         x["link_count"] = links_count.get(x["id"]) or 0
    #     return data

    def instance_to_dict(self, o, fields=None):
        def sg_to_list(items):
            return [
                {"group": x, "group__label": smart_text(ResourceGroup.get_by_id(x))} for x in items
            ]

        data = super().instance_to_dict(o, fields)
        # Expand resource groups fields
        for fn in self.resource_group_fields:
            data[fn] = sg_to_list(data.get(fn) or [])
        data["is_managed"] = getattr(o, "is_managed", True)
        data["is_wiping"] = o.state.is_wiping
        data["diagnostics"] = []
        for d in sorted(o.diagnostic, key=lambda x: x.config.display_order):
            if not d.config.show_in_display:
                continue
            data["diagnostics"].append(
                {
                    "name": d.diagnostic[:6],
                    "description": d.config.display_description,
                    "state": d.state.value,
                    "state__label": d.state.value,
                    "details": [
                        {
                            "name": c.name,
                            "state": {True: "OK", False: "Error"}[c.status],
                            "error": c.error,
                        }
                        for c in d.checks or []
                        if not c.skipped
                    ],
                    "reason": d.reason or "",
                }
            )
        for m in data["mappings"]:
            rs = RemoteSystem.get_by_id(m["remote_system"])
            m |= {
                "remote_system__label": rs.name,
                "is_master": False,
                "url": None,
            }
            if rs.object_url_template:
                m["url"] = rs.object_url_template
        if o.remote_system:
            data["mappings"].append(
                {
                    "remote_system": str(o.remote_system.id),
                    "remote_system__label": o.remote_system.name,
                    "remote_id": o.remote_id,
                    "url": None,
                    "is_master": False,
                }
            )
        return data

    def instance_to_dict_list(self, o: "ManagedObject", fields=None):
        """

        :param o:
        :param fields:
        :return:
        """
        if not o.is_managed or not o.object_profile.enable_ping:
            ostate = "disabled"
            ostate_label = _("Disable")
        elif not o.get_status():
            ostate = "failed"
            ostate_label = _("Down")
        else:
            ostate = "full"
            ostate_label = _("Up")
        return {
            "id": o.id,
            "name": o.name,
            "address": o.address,
            "oper_state": ostate,
            "oper_state__label": ostate_label,
            "is_managed": getattr(o, "is_managed", True),
            "administrative_domain": str(o.administrative_domain.name),
            "object_profile": str(o.object_profile.name),
            "segment": str(o.segment.name),
            "auth_profile": str(o.auth_profile.name) if o.auth_profile else "",
            "profile": o.profile.name,
            "state": str(o.state),
            "pool": str(o.pool.name),
            "platform": o.platform.name if o.platform else "",
            "version": o.version.version if o.version else "",
            "vrf": o.vrf.name if o.vrf else "",
            "description": o.description or "",
            "row_class": o.object_profile.style.css_class_name if o.object_profile.style else "",
            "link_count": len(o.links),
            "labels": sorted(
                [self.format_label(ll) for ll in Label.from_names(o.labels)],
                key=lambda x: x["display_order"],
            ),
            # "row_class": ""
        }

    def clean(self, data):
        # Clean resource groups
        for fn in self.resource_group_fields:
            if fn.startswith("effective_") and fn in data:
                del data[fn]
                continue
            data[fn] = [x["group"] for x in (data.get(fn) or [])]
        # Ignore on Save Fields
        for f in ManagedObject._ignore_on_save:
            if f in data:
                del data[f]
        # Ignore Effective labes field
        if "effective_labels" in data:
            del data["effective_labels"]
        # Clean other
        return super().clean(data)

    def cleaned_query(self, q):
        geoaddr = q.pop("__geoaddress", None)
        if "administrative_domain" in q:
            ad = AdministrativeDomain.get_nested_ids(int(q["administrative_domain"]))
            if ad:
                del q["administrative_domain"]
        else:
            ad = None
        r = super().cleaned_query(q)
        if ad:
            r["administrative_domain__in"] = ad
        if geoaddr:
            scope, query = geoaddr.split(":", 1)
            geocoder = geocoder_loader.get_class(scope)()
            addr_ids = set([r.id for r in geocoder.iter_recursive_query(query)][:1])
            addr_mo = set()
            for o in Object.iter_by_address_id(list(addr_ids), scope):
                addr_mo |= set(o.iter_managed_object_id())
                # If ManagedObject has container refer to Object
                addr_mo |= set(
                    ManagedObject.objects.filter(container__in=o.get_nested_ids()).values_list(
                        "id", flat=True
                    )
                )
            r["id__in"] = list(addr_mo)
        if "addresses" in r:
            if isinstance(r["addresses"], list):
                r["address__in"] = r["addresses"]
            else:
                r["address__in"] = [r["addresses"]]
            del r["addresses"]
        # Clean Caps
        for f in list(r):
            if f and f.startswith("caps"):
                r.pop(f)
        if "is_managed" in q:
            del q["is_managed"]
        return r

    def extra_query(self, q, order):
        # raise NotImplementedError
        extra, order = super().extra_query(q, order)
        _, extra_condition = self.get_caps_Q(q)
        if extra_condition:
            extra["where"] = extra_condition
        return extra, order

    def get_caps_Q(self, nq: Dict[str, Any]) -> Tuple["d_Q", List[str]]:
        """
        Resolve caps on query to queryset
        :param nq:
        :return:
        """
        q, jp_clauses = d_Q(), []
        for cc in [part for part in nq if part.startswith("caps")]:
            """
            Caps: caps0=CapsID,caps1=CapsID:true....
            cq - caps query
            mq - main_query
            caps0=CapsID - caps is exists
            caps0=!CapsID - caps is not exists
            caps0=CapsID:true - caps value equal True
            caps0=CapsID:2~50 - caps value many then 2 and less then 50
            """
            c = nq.get(cc)
            if not c or cc in self.clean_fields:
                continue

            if "!" in c:
                # @todo Добавить исключение (только этот) !ID
                c_id = c[1:]
                c_query = "nexists"
            elif ":" not in c:
                c_id = c
                c_query = "exists"
            else:
                c_id, c_query = c.split(":", 1)
            if not is_objectid(c_id):
                continue
            caps = Capability.get_by_id(c_id)
            self.logger.info("[%s] Caps: %s", c, caps)
            if "~" in c_query:
                l, r = c_query.split("~")
                if not l:
                    jp_clauses.append(JP_CLAUSE_PATTERN.format(caps.id, "<=", r))
                elif not r:
                    jp_clauses.append(JP_CLAUSE_PATTERN.format(caps.id, ">=", l))
                else:
                    # TODO This functionality is not implemented in frontend
                    jp_clauses.append(JP_CLAUSE_PATTERN.format(caps.id, "<=", r))
                    jp_clauses.append(JP_CLAUSE_PATTERN.format(caps.id, ">=", l))
            elif c_query in ("false", "true"):
                q &= d_Q(caps__contains=[{"capability": str(caps.id), "value": c_query == "true"}])
            elif c_query == "exists":
                q &= d_Q(caps__contains=[{"capability": str(caps.id)}])
                continue
            elif c_query == "nexists":
                q &= ~d_Q(caps__contains=[{"capability": str(caps.id)}])
                continue
            else:
                value = caps.clean_value(c_query)
                q &= d_Q(caps__contains=[{"capability": str(caps.id), "value": value}])
        return q, jp_clauses

    def get_Q(self, request, query):
        q = super().get_Q(request, query)
        sq = ManagedObject.get_search_Q(query)
        if sq:
            q |= sq
        return q

    def queryset(self, request, query=None):
        qs = super().queryset(request, query)
        if not request.user.is_superuser:
            qs = qs.filter(UserAccess.Q(request.user))
        cq, _ = self.get_caps_Q(self.parse_request_query(request))
        if cq:
            qs = qs.filter(cq)
        # qs = qs.exclude(name__startswith="wiping-")
        # Filter Wiped
        # w_states = Workflow.get_wiping_states()
        # if w_states:
        #    qs = qs.exclude(state__in=[str(s) for s in w_states])
        return qs

    @view(url=r"^(?P<id>\d+)/links/$", method=["GET"], access="read", api=True)
    def api_links(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        # Get links
        result = []
        for link in Link.object_links(o):
            ifaces = []
            r = []
            for i in link.interfaces:
                if i.managed_object.id == o.id:
                    ifaces += [i]
                else:
                    r += [i]
            for li, ri in zip(ifaces, r):
                result += [
                    {
                        "link_id": str(link.id),
                        "local_interface": str(li.id),
                        "local_interface__label": li.name,
                        "remote_object": ri.managed_object.id,
                        "remote_object__label": ri.managed_object.name,
                        "remote_platform": (
                            ri.managed_object.platform.name if ri.managed_object.platform else ""
                        ),
                        "remote_interface": str(ri.id),
                        "remote_interface__label": ri.name,
                        "discovery_method": link.discovery_method,
                        "local_description": li.description,
                        "remote_description": ri.description,
                        "first_discovered": (
                            link.first_discovered.isoformat() if link.first_discovered else None
                        ),
                        "last_seen": link.last_seen.isoformat() if link.last_seen else None,
                    }
                ]
        return result

    @view(url=r"^(?P<id>\d+)/discovery/$", method=["GET"], access="read", api=True)
    def api_discovery(self, request, id):
        from noc.core.scheduler.job import Job

        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        link_count = defaultdict(int)
        for link in Link.object_links(o):
            m = link.discovery_method or ""
            if "+" in m:
                m = m.split("+")[0]
            link_count[m] += 1
        r = [
            {
                "name": "ping",
                "enable_profile": o.object_profile.enable_ping,
                "status": o.get_status(),
                "last_run": None,
                "last_status": None,
                "next_run": None,
                "jcls": None,
            }
        ]

        for name, jcls in self.DISCOVERY_JOBS:
            job = Job.get_job_data("discovery", jcls=jcls, key=o.id, pool=o.pool.name) or {}
            if name == "box" and Interaction.BoxDiscovery not in o.interactions:
                enable = False
            elif name == "periodic":
                enable = Interaction.BoxDiscovery in o.interactions and (
                    getattr(o.object_profile, "enable_metrics")
                    or getattr(o.object_profile, f"enable_{name}_discovery")
                )
            else:
                enable = getattr(o.object_profile, f"enable_{name}_discovery")
            d = {
                "name": name,
                "enable_profile": enable,
                "status": job.get(Job.ATTR_STATUS),
                "last_run": self.to_json(job.get(Job.ATTR_LAST)),
                "last_status": job.get(Job.ATTR_LAST_STATUS),
                "next_run": self.to_json(job.get(Job.ATTR_TS)),
                "jcls": jcls,
            }
            r += [d]
        return r

    @view(
        url=r"^actions/set_managed/$",
        method=["POST"],
        access="create",
        api=True,
        validate={"ids": ListOfParameter(element=ModelParameter(ManagedObject), convert=True)},
    )
    def api_action_set_managed(self, request, ids):
        for o in ids:
            if not o.has_access(request.user):
                continue
            o.fire_event("managed")
            o.save()
        return "Selected objects set to managed state"

    @view(
        url=r"^actions/set_unmanaged/$",
        method=["POST"],
        access="create",
        api=True,
        validate={"ids": ListOfParameter(element=ModelParameter(ManagedObject), convert=True)},
    )
    def api_action_set_unmanaged(self, request, ids):
        for o in ids:
            if not o.has_access(request.user):
                continue
            o.fire_event("unmanaged")
            o.save()
        return "Selected objects set to unmanaged state"

    @view(url=r"^(?P<id>\d+)/discovery/run/$", method=["POST"], access="change_discovery", api=True)
    def api_run_discovery(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = orjson.loads(request.body).get("names", [])
        shard, d_slots = None, config.get_slot_limits(f"discovery-{o.pool.name}")
        if d_slots:
            shard = o.id % d_slots
        for name, jcls in self.DISCOVERY_JOBS:
            if name not in r:
                continue
            elif name == "box" and Interaction.BoxDiscovery not in o.interactions:
                continue
            elif name == "periodic" and Interaction.PeriodicDiscovery not in o.interactions:
                continue
            elif name == "periodic" and not (
                getattr(o.object_profile, f"enable_{name}_discovery")
                or getattr(o.object_profile, "enable_metrics")
            ):
                continue
            elif not getattr(o.object_profile, f"enable_{name}_discovery", None):
                continue  # Disabled by profile
            Job.submit("discovery", jcls, key=o.id, pool=o.pool.name, shard=shard)
        return {"success": True}

    @view(
        url=r"^(?P<id>\d+)/discovery/stop/$", method=["POST"], access="change_discovery", api=True
    )
    def api_stop_discovery(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = orjson.loads(request.body).get("names", [])
        for name, jcls in self.DISCOVERY_JOBS:
            if name not in r:
                continue
            elif name == "box" and Interaction.BoxDiscovery not in o.interactions:
                continue
            elif name == "periodic" and Interaction.PeriodicDiscovery not in o.interactions:
                continue
            elif name == "periodic" and not (
                getattr(o.object_profile, f"enable_{name}_discovery")
                or getattr(o.object_profile, "enable_metrics")
            ):
                continue
            elif not getattr(o.object_profile, f"enable_{name}_discovery"):
                continue  # Disabled by profile
            Job.remove("discovery", jcls, key=o.id, pool=o.pool.name)
        return {"success": True}

    @view(url=r"^(?P<id>\d+)/interface/$", method=["GET"], access="read", api=True)
    def api_interface(self, request, id):
        """
        GET interfaces
        :param managed_object:
        :return:
        """

        def sorted_iname(s):
            return list(sorted(s, key=lambda x: alnum_key(x["name"])))

        def get_style(i):
            profile = i.profile
            if profile:
                try:
                    return style_cache[profile.id]
                except KeyError:
                    pass
                if profile.style:
                    s = profile.style.css_class_name
                else:
                    s = ""
                style_cache[profile.id] = s
                return s
            else:
                return ""

        def get_link(i):
            link = i.link
            if not link:
                return None
            if link.is_ptp:
                # ptp
                o = link.other_ptp(i)
                label = "%s:%s" % (o.managed_object.name, o.name)
            elif link.is_lag:
                # unresolved LAG
                o = [ii for ii in link.other(i) if ii.managed_object.id != i.managed_object.id]
                label = "LAG %s: %s" % (o[0].managed_object.name, ", ".join(ii.name for ii in o))
            else:
                # Broadcast
                label = ", ".join(
                    "%s:%s" % (ii.managed_object.name, ii.name) for ii in link.other(i)
                )
            return {"id": str(link.id), "label": label}

        # Get object
        o = self.get_object_or_404(ManagedObject, id=int(id))
        if not o.has_access(request.user):
            return self.response_forbidden("Permission denied")
        metrics = {}
        if o.object_profile.enable_metrics:
            r, _ = get_interface_metrics(managed_objects=[o.bi_id], metrics=self.x_map)
            for iface in r[o.bi_id]:
                ctx = {m: "--" for m in self.x_map}
                ctx.update(r[o.bi_id][iface])
                ctx["load_in"] = "%.2f%s" % Scale.humanize(int(r[o.bi_id][iface]["load_in"]))
                ctx["load_out"] = "%.2f%s" % Scale.humanize(int(r[o.bi_id][iface]["load_out"]))
                metrics[iface] = self.iface_metric_template.render(**ctx)
        # Physical interfaces
        # @todo: proper ordering
        style_cache = {}  # profile_id -> css_style
        l1 = [
            {
                "id": str(i.id),
                "name": i.name,
                "description": i.description,
                "status": i.status,
                "mac": i.mac,
                "ifindex": i.ifindex,
                "lag": (i.aggregated_interface.name if i.aggregated_interface else ""),
                "link": get_link(i),
                "metrics": metrics.get(i.name, ""),
                "profile": str(i.profile.id) if i.profile else None,
                "profile__label": smart_text(i.profile) if i.profile else None,
                "enabled_protocols": i.enabled_protocols,
                "project": i.project.id if i.project else None,
                "project__label": smart_text(i.project) if i.project else None,
                "state": str(i.state.id) if i.state else None,
                "state__label": smart_text(i.state) if i.state else None,
                "row_class": get_style(i),
            }
            for i in Interface.objects.filter(managed_object=o.id, type="physical")
        ]
        # LAG
        lag = [
            {
                "id": str(i.id),
                "name": i.name,
                "status": i.status,
                "description": i.description,
                "profile": str(i.profile.id) if i.profile else None,
                "profile__label": smart_text(i.profile) if i.profile else None,
                "members": [
                    j.name
                    for j in Interface.objects.filter(
                        managed_object=o.id, aggregated_interface=i.id
                    )
                ],
                "row_class": get_style(i),
            }
            for i in Interface.objects.filter(managed_object=o.id, type="aggregated")
        ]
        # L2 interfaces
        l2 = [
            {
                "name": i.name,
                "description": i.description,
                "untagged_vlan": i.untagged_vlan,
                "tagged_vlans": i.tagged_vlans,
            }
            for i in SubInterface.objects.filter(managed_object=o.id, enabled_afi="BRIDGE")
        ]
        # L3 interfaces
        q = MQ(enabled_afi="IPv4") | MQ(enabled_afi="IPv6")
        l3 = [
            {
                "name": i.name,
                "description": i.description,
                "ipv4_addresses": i.ipv4_addresses,
                "ipv6_addresses": i.ipv6_addresses,
                "enabled_protocols": i.enabled_protocols,
                "vlan": i.vlan_ids,
                "vrf": i.forwarding_instance.name if i.forwarding_instance else "",
                "mac": i.mac,
            }
            for i in SubInterface.objects.filter(managed_object=o.id).filter(q)
        ]
        return {
            "l1": sorted_iname(l1),
            "lag": sorted_iname(lag),
            "l2": sorted_iname(l2),
            "l3": sorted_iname(l3),
        }

    @view(
        url=r"^(?P<id>\d+)/interface/(?P<if_id>[0-9a-f]{24})/$",
        method=["DELETE"],
        access="change_interface",
        api=True,
    )
    def api_delete_interface(self, request, id, if_id):
        o = self.get_object_or_404(ManagedObject, id=int(id))
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        iface = Interface.objects.filter(managed_object=int(id), id=if_id).first()
        if iface:
            iface.delete()
        return {"success": True}

    @view(url=r"^(?P<id>\d+)/interface/$", method=["POST"], access="change_interface", api=True)
    def api_set_interface(self, request, id):
        def get_or_none(c, v):
            if not v:
                return None
            return c.objects.get(id=v)

        o = self.get_object_or_404(ManagedObject, id=int(id))
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        d = orjson.loads(request.body)
        if "id" in d:
            i = self.get_object_or_404(Interface, id=d["id"])
            if i.managed_object.id != o.id:
                return self.response_not_found()
        else:
            i = Interface(managed_object=o.id, type="physical")
        # Set name
        if "name" in d:
            i.name = o.get_profile().convert_interface_name(d["name"])
        if "description" in d:
            i.description = d["description"].strip()
        # Set profile
        if "profile" in d:
            p = get_or_none(InterfaceProfile, d["profile"])
            i.profile = p
            if p:
                i.profile_locked = True
        # Project
        if "project" in d:
            i.project = get_or_none(Project, d["project"])
        #
        i.save()
        return {"success": True}

    @view(method=["DELETE"], url=r"^(?P<id>\d+)/?$", access="delete", api=True)
    def api_delete(self, request, id):
        """
        Override default method
        :param request:
        :param id:
        :return:
        """
        try:
            o = self.queryset(request).get(id=int(id))
        except self.model.DoesNotExist:
            return self.render_json(
                {"status": False, "message": "Not found"}, status=self.NOT_FOUND
            )
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        ws = o.object_profile.workflow.get_wiping_state()
        if not ws:
            return HttpResponse(
                orjson.dumps({"status": False, "message": "No wiping state on Workflow"}),
                status=self.FORBIDDEN,
            )
        o.set_state(ws)
        return HttpResponse(orjson.dumps({"status": True}), status=self.DELETED)

    @view(
        url=r"^actions/run_discovery/$",
        method=["POST"],
        access="launch",
        api=True,
        validate={"ids": ListOfParameter(element=ModelParameter(ManagedObject), convert=True)},
    )
    def api_action_run_discovery(self, request, ids):
        d = 0
        for o in ids:
            if not o.has_access(request.user):
                continue
            o.run_discovery(delta=d)
            d += 1
        return "Discovery processes has been scheduled"

    def get_nested_inventory(self, o: "Object"):
        rev = o.get_data("asset", "revision")
        if rev == "None":
            rev = ""
        r = {
            "id": str(o.id),
            "serial": o.get_data("asset", "serial"),
            "revision": rev or "",
            "description": o.model.description,
            "model": o.model.name,
        }
        if o.is_generic_transceiver:
            # Generate description by template
            # 1000Base-BX SFP Transceiver (SMF, 1490nmTx/1550nmRx, 80km, LC, DOM)
            optical_data = {
                d.attr: d.value for d in o.get_effective_data() if d.interface == "optical"
            }
            if "tx_wavelength" in optical_data:
                description = ["SMF"]
                if (
                    "rx_wavelength" in optical_data
                    and optical_data["tx_wavelength"] != optical_data["rx_wavelength"]
                ):
                    description += [
                        f'{optical_data["tx_wavelength"]}nmTx/{optical_data["rx_wavelength"]}nmRx'
                    ]
                else:
                    description += [f'{optical_data["tx_wavelength"]}nmTx']
                if "distance_max" in optical_data:
                    description += [f'{optical_data["distance_max"]}km']
                description += ["LC", "DOM"]
                r["description"] = f"SFP Transceiver ({', '.join(description)})"
                if "bit_rate" in optical_data:
                    r["description"] = f"{optical_data['bit_rate']}Base " + r["description"]
        if_map = {c.name: c.interface_name for c in o.connections}
        children = []
        for n in o.model.connections:
            if n.direction == "i":
                c, r_object, _ = o.get_p2p_connection(n.name)
                if c is None:
                    children += [
                        {
                            "id": None,
                            "name": n.name,
                            "leaf": True,
                            "serial": None,
                            "description": "--- EMPTY ---",
                            "model": None,
                            "interface": if_map.get(n.name) or "",
                        }
                    ]
                else:
                    cc = self.get_nested_inventory(r_object)
                    cc["name"] = n.name
                    cc["interface"] = if_map.get(n.name) or ""
                    children += [cc]
            elif n.direction == "s":
                children += [
                    {
                        "id": None,
                        "name": n.name,
                        "leaf": True,
                        "serial": None,
                        "description": n.description,
                        "model": ", ".join(str(p) for p in n.protocols),
                        "interface": if_map.get(n.name) or "",
                    }
                ]
        if children:
            to_expand = "Transceiver" not in o.model.name
            r["children"] = children
            r["expanded"] = to_expand
        else:
            r["leaf"] = True
        return r

    @view(url=r"^(?P<id>\d+)/inventory/$", method=["GET"], access="read", api=True)
    def api_inventory(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = []
        for p in o.get_inventory():
            c = self.get_nested_inventory(p)
            c["name"] = p.name or o.name
            r += [c]
        return {"expanded": True, "children": r}

    @view(url=r"^(?P<id>\d+)/confdb/$", method=["GET"], access="config", api=True)
    def api_confdb(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        cleanup = True
        if "cleanup" in request.GET:
            c = request.GET["cleanup"].strip().lower()
            cleanup = c not in ("no", "false", "0")
        cdb = o.get_confdb(cleanup=cleanup)
        return self.render_plain_text(cdb.dump("json"), content_type="text/json")

    @view(
        url=r"^(?P<id>\d+)/confdb/$",
        method=["POST"],
        validate={
            "query": StringParameter(),
            "cleanup": BooleanParameter(default=True),
            "dump": BooleanParameter(default=False),
        },
        access="config",
        api=True,
    )
    def api_confdb_query(self, request, id, query="", cleanup=True, dump=False):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        cdb = o.get_confdb(cleanup=cleanup)
        try:
            r = list(cdb.query(query))
            result = {"status": True, "result": r}
            if dump:
                result["confdb"] = orjson.loads(cdb.dump("json"))
        except SyntaxError as e:
            result = {"status": False, "error": str(e)}
        return result

    @view(url=r"^(?P<id>\d+)/job_log/(?P<job>\S+)/$", method=["GET"], access="read", api=True)
    def api_job_log(self, request, id, job):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        # fs = gridfs.GridFS(get_db(), "noc.joblog")
        key = "discovery-%s-%s" % (job, o.id)
        d = get_db()["noc.joblog"].find_one({"_id": key})
        if d and d["log"]:
            return self.render_plain_text(zlib.decompress(smart_bytes((d["log"]))))
        else:
            return self.render_plain_text("No data")

    @view(url=r"^(?P<id>\d+)/interactions/$", method=["GET"], access="interactions", api=True)
    def api_interactions(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        return [
            {"ts": self.to_json(i.timestamp), "op": i.op, "user": i.user, "text": i.text}
            for i in InteractionLog.objects.filter(object=o.id).order_by("-timestamp")
        ]

    @view(url=r"^(?P<id>\d+)/scripts/$", method=["GET"], access="script", api=True)
    def api_scripts(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = []
        for s in o.scripts:
            sn = o.profile.name + "." + s
            script = script_loader.get_script(sn)
            if not script:
                self.logger.error("Failed to load script: %s", sn)
                continue
            interface = script.interface()
            ss = {
                "name": s,
                "has_input": any(interface.gen_parameters()),
                "require_input": interface.has_required_params,
                "form": interface.get_form(),
                "preview": interface.preview or "NOC.sa.managedobject.scripts.JSONPreview",
            }
            r += [ss]
        return r

    @view(url=r"^(?P<id>\d+)/scripts/(?P<name>[^/]+)/$", method=["POST"], access="script", api=True)
    def api_run_script(self, request, id, name):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return {"error": "Access denied"}
        if name not in o.scripts:
            return {"error": "Script not found: %s" % name}
        params = self.deserialize(request.body)
        try:
            result = o.scripts[name](**params)
        except Exception as e:
            return {"error": str(e)}
        return {"result": result}

    @view(url=r"^(?P<id>\d+)/console/$", method=["POST"], access="console", api=True)
    def api_console_command(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return {"error": "Access denied"}
        if "commands" not in o.scripts:
            return {"error": "Script not found: commands"}
        params = self.deserialize(request.body)
        try:
            result = o.scripts.commands(**params)
        except Exception as e:
            return {"error": str(e)}
        return {"result": result}

    @view(url=r"(?P<id>\d+)/caps/$", method=["GET"], access="read", api=True)
    def api_get_caps(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = []
        if o.caps:
            for c in o.caps:
                capability = Capability.get_by_id(c["capability"])
                r += [
                    {
                        "capability": capability.name,
                        "description": capability.description,
                        "type": capability.type,
                        "value": c["value"],
                        "source": c["source"],
                        "scope": c.get("scope", ""),
                    }
                ]
        return sorted(r, key=lambda x: x["capability"])

    @view(url=r"(?P<id>\d+)/actions/(?P<action>\S+)/$", method=["POST"], access="action", api=True)
    def api_action(self, request, id, action):
        def execute(o, a, args):
            return a.execute(o, **args)

        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        a = self.get_object_or_404(Action, name=action)
        # @todo: Check access
        if request.body:
            args = orjson.loads(request.body)
        else:
            args = {}
        return self.submit_slow_op(request, execute, o, a, args)

    @view(
        url=r"(?P<id>\d+)/mappings/$",
        method=["POST"],
        access="change_mappings",
        api=True,
        validate={
            "mappings": DictListParameter(
                attrs={
                    "remote_system": DocumentParameter(RemoteSystem, required=True),
                    "remote_id": StringParameter(required=True),
                }
            )
        },
    )
    def api_update_mappings(self, request, id, mappings):
        o = self.get_object_or_404(ManagedObject, id=id)
        mappings = {m["remote_system"]: m["remote_id"] for m in mappings}
        o.update_object_mappings(mappings)
        return {"status": True}

    @view(url=r"^link/fix/(?P<link_id>[0-9a-f]{24})/$", method=["POST"], access="change_link")
    def api_fix_links(self, request, link_id):
        def get_mac(arp, ip):
            for r in arp:
                if r["ip"] == ip:
                    return r["mac"]
            return None

        def get_interface(macs, mac):
            for m in macs:
                if m["mac"] == mac:
                    return m["interfaces"][0]
            return None

        def error_status(message, *args):
            self.logger.error(message, *args)
            return {"status": False, "message": message % args}

        def success_status(message, *args):
            self.logger.error(message, *args)
            return {"status": True, "message": message % args}

        link = self.get_object_or_404(Link, id=link_id)
        if len(link.interfaces) != 2:
            return error_status("Cannot fix link: Not P2P")
        mo1 = link.interfaces[0].managed_object
        mo2 = link.interfaces[1].managed_object
        if mo1.id == mo2.id:
            return error_status("Cannot fix circular links")
        # Ping each other
        self.logger.info("[%s] Pinging %s", mo1.name, mo2.address)
        r1 = mo1.scripts.ping(address=mo2.address)
        if not r1["success"]:
            return error_status("Failed to ping %s", mo2.name)
        self.logger.info("[%s] Pinging %s", mo2.name, mo1.address)
        r2 = mo2.scripts.ping(address=mo1.address)
        if not r2["success"]:
            return error_status("Failed to ping %s", mo1.name)
        # Get ARPs
        mac2 = get_mac(mo1.scripts.get_arp(), mo2.address)
        if not mac2:
            return error_status("[%s] ARP cache is not filled properly", mo1.name)
        self.logger.info("[%s] MAC=%s", mo2.name, mac2)
        mac1 = get_mac(mo2.scripts.get_arp(), mo1.address)
        if not mac1:
            return error_status("[%s] ARP cache is not filled properly", mo2.name)
        self.logger.info("[%s] MAC=%s", mo1.name, mac1)
        # Get MACs
        r1 = mo1.scripts.get_mac_address_table(mac=mac2)
        self.logger.info("[%s] MACS=%s", mo1.name, r1)
        r2 = mo2.scripts.get_mac_address_table(mac=mac1)
        self.logger.info("[%s] MACS=%s", mo2.name, r2)
        # mo1: Find mo2
        i1 = get_interface(r1, mac2)
        if not i1:
            return error_status("[%s] Cannot find %s in the MAC address table", mo1.name, mo2.name)
        # mo2: Find mo1
        i2 = get_interface(r2, mac1)
        if not i1:
            return error_status("[%s] Cannot find %s in the MAC address table", mo2.name, mo1.name)
        self.logger.info("%s:%s -- %s:%s", mo1.name, i1, mo2.name, i2)
        if link.interfaces[0].name == i1 and link.interfaces[1].name == i2:
            return success_status("Linked properly")
        # Get interfaces
        iface1 = mo1.get_interface(i1)
        if not iface1:
            return error_status("[%s] Interface not found: %s", mo1.name, i1)
        iface2 = mo2.get_interface(i2)
        if not iface2:
            return error_status("[%s] Interface not found: %s", mo2.name, i2)
        # Check we can relink
        if_ids = [i.id for i in link.interfaces]
        if iface1.id not in if_ids and iface1.is_linked:
            return error_status("[%s] %s is already linked", mo1.name, i1)
        if iface2.id not in if_ids and iface2.is_linked:
            return error_status("[%s] %s is already linked", mo2.name, i2)
        # Relink
        self.logger.info("Relinking")
        link.delete()
        iface1.link_ptp(iface2, method="macfix")
        return success_status("Relinked")

    @view(url=r"^(?P<id>\d+)/cpe/$", method=["GET"], access="read", api=True)
    def api_cpe(self, request, id):
        """
        GET CPEs
        :param request:
        :param id:
        :return:
        """

        def sorted_iname(s):
            return list(sorted(s, key=lambda x: alnum_key(x["name"])))

        # Get object
        o = self.get_object_or_404(ManagedObject, id=int(id))
        if not o.has_access(request.user):
            return self.response_forbidden("Permission denied")
        # CPE
        # @todo: proper ordering
        # default_state = ResourceState.get_default()
        # style_cache = {}  # profile_id -> css_style
        l1 = [
            {
                "global_id": str(c.global_id),
                "name": c.name or "",
                "interface": c.interface,
                "local_id": c.local_id,
                "serial": c.serial or "",
                "status": c.status,
                "description": c.description or "",
                "address": c.ip or "",
                "model": c.model or "",
                "version": c.version or "",
                "mac": c.mac or "",
                "location": c.location or "",
                "distance": str(c.distance),
                # "row_class": get_style(i)
            }
            for c in CPEStatus.objects.filter(managed_object=o.id)
        ]

        return {"cpe": sorted_iname(l1)}

    def has_repo_config_access(self, user, obj):
        """
        Check user has access to object

        :param user: User instance
        :param obj: ManagedObject instance
        :return: True if user has access, False otherwise
        """
        if user.is_superuser:
            return True
        return ManagedObject.objects.filter(id=obj.id).filter(UserAccess.Q(user)).exists()

    @view(url=r"^(?P<id>\d+)/map_lookup/$", method=["GET"], access="read", api=True)
    def api_map_lookup(self, request, id):
        o: ManagedObject = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = [
            {
                "id": str(o.id),
                "label": _("Topology Neighbors"),
                "is_default": False,
                "args": ["objectlevelneighbor", str(o.id), o.id],
            }
        ]
        if o.segment:
            r += [
                {
                    "id": str(o.segment.id),
                    "label": _("Segment: ") + str(o.segment.name),
                    "is_default": True,
                    "args": ["segment", str(o.segment.id), o.id],
                }
            ]
        if o.container:
            r += [
                {
                    "id": str(o.container.id),
                    "label": _("Container: ") + str(o.container.name),
                    "is_default": False,
                    "args": ["objectcontainer", str(o.container.id), o.id],
                }
            ]
        return r

    @view(url=r"^full/", method=["GET", "POST"], access="read", api=True)
    def api_list_full(self, request):
        try:
            return self.list_data(request, self.instance_to_dict)
        except Exception as e:
            error_report()
            return self.response({"status": False, "message": str(e)}, status=self.INTERNAL_ERROR)

    @view(url=r"^list/", method=["GET", "POST"], access="read", api=True)
    def api_list_short(self, request):
        try:
            return self.list_data(request, self.instance_to_dict_list)
        except Exception as e:
            error_report()
            return self.response({"status": False, "message": str(e)}, status=self.INTERNAL_ERROR)
