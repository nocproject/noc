# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.managedobject application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import zlib
# Django modules
from django.http import HttpResponse
# Third-party modules
import ujson
from mongoengine.queryset import Q as MQ
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.managedobject import (ManagedObject,
                                         ManagedObjectAttribute)
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.interactionlog import InteractionLog
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.profile import Profile
from noc.inv.models.link import Link
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.lib.app.modelinline import ModelInline
from noc.lib.app.repoinline import RepoInline
from noc.lib.app.decorators.handlerfield import handler_field
from noc.main.models.resourcestate import ResourceState
from noc.project.models.project import Project
from noc.vc.models.vcdomain import VCDomain
from noc.sa.models.objectcapabilities import ObjectCapabilities
from noc.lib.text import split_alnum
from noc.sa.interfaces.base import ListOfParameter, ModelParameter
from noc.cm.models.objectfact import ObjectFact
from noc.cm.engine import Engine
from noc.sa.models.action import Action
from noc.core.scheduler.job import Job
from noc.core.script.loader import loader as script_loader
from noc.lib.nosql import get_db
from noc.core.defer import call_later
from noc.core.translation import ugettext as _


@handler_field(
    "config_filter_handler",
    "config_diff_filter_handler",
    "config_validation_handler"
)
class ManagedObjectApplication(ExtModelApplication):
    """
    ManagedObject application
    """
    title = _("Managed Objects")
    menu = _("Managed Objects")
    model = ManagedObject
    query_condition = "icontains"
    query_fields = ["name", "description"]
    # Inlines
    attrs = ModelInline(ManagedObjectAttribute)
    cfg = RepoInline("config")

    extra_permissions = ["alarm", "change_interface"]
    implied_permissions = {
        "read": [
            "inv:networksegment:lookup",
            "main:handler:lookup"
        ]
    }
    order_map = {
        "address": " cast_test_to_inet(address) ",
        "-address": " cast_test_to_inet(address) ",
        "profile": 'CASE %s END' % ' '.join(['WHEN %s=\'%s\' THEN %s' % ("profile", pk, i) for i, pk in enumerate(
            Profile.objects.filter().order_by("name").values_list("id"))]),
        "-profile": 'CASE %s END' % ' '.join(['WHEN %s=\'%s\' THEN %s' % ("profile", pk, i) for i, pk in enumerate(
            Profile.objects.filter().order_by("-name").values_list("id"))]),
        "platform": 'CASE %s END' % ' '.join(['WHEN %s=\'%s\' THEN %s' % ("platform", pk, i) for i, pk in enumerate(
            Platform.objects.filter().order_by("name").values_list("id"))]),
        "-platform": 'CASE %s END' % ' '.join(['WHEN %s=\'%s\' THEN %s' % ("platform", pk, i) for i, pk in enumerate(
            Platform.objects.filter().order_by("-name").values_list("id"))]),
        "version": 'CASE %s END' % ' '.join(['WHEN %s=\'%s\' THEN %s' % ("version", pk, i) for i, pk in enumerate(
            Firmware.objects.filter().order_by("version").values_list("id"))]),
        "-version": 'CASE %s END' % ' '.join(['WHEN %s=\'%s\' THEN %s' % ("version", pk, i) for i, pk in enumerate(
            Firmware.objects.filter().order_by("-version").values_list("id"))])
    }

    DISCOVERY_JOBS = [
        ("box", "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"),
        ("periodic", "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob")
    ]

    def field_row_class(self, o):
        return o.object_profile.style.css_class_name if o.object_profile.style else ""

    def field_interface_count(self, o):
        return Interface.objects.filter(
            managed_object=o.id,
            type="physical"
        ).count()

    def field_link_count(self, o):
        return Link.object_links_count(o)

    def cleaned_query(self, q):
        if "administrative_domain" in q:
            ad = AdministrativeDomain.get_nested_ids(
                int(q["administrative_domain"])
            )
            if ad:
                del q["administrative_domain"]
        else:
            ad = None
        if "selector" in q:
            s = self.get_object_or_404(ManagedObjectSelector,
                                       id=int(q["selector"]))
            del q["selector"]
        else:
            s = None
        r = super(ManagedObjectApplication, self).cleaned_query(q)
        if s:
            r["id__in"] = ManagedObject.objects.filter(s.Q)
        if ad:
            r["administrative_domain__in"] = ad
        return r

    def get_Q(self, request, query):
        q = super(ManagedObjectApplication, self).get_Q(request, query)
        sq = ManagedObject.get_search_Q(query)
        if sq:
            q |= sq
        return q

    def queryset(self, request, query=None):
        qs = super(ManagedObjectApplication, self).queryset(request, query)
        if not request.user.is_superuser:
            qs = qs.filter(UserAccess.Q(request.user))
        qs = qs.exclude(name__startswith="wiping-")
        return qs

    @view(url="^(?P<id>\d+)/links/$", method=["GET"],
          access="read", api=True)
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
                result += [{
                    "link_id": str(link.id),
                    "local_interface": str(li.id),
                    "local_interface__label": li.name,
                    "remote_object": ri.managed_object.id,
                    "remote_object__label": ri.managed_object.name,
                    "remote_platform": ri.managed_object.platform.name if ri.managed_object.platform else "",
                    "remote_interface": str(ri.id),
                    "remote_interface__label": ri.name,
                    "discovery_method": link.discovery_method,
                    "local_description": li.description,
                    "remote_description": ri.description,
                    "first_discovered": link.first_discovered.isoformat() if link.first_discovered else None,
                    "last_seen": link.last_seen.isoformat() if link.last_seen else None
                }]
        return result

    @view(url="^(?P<id>\d+)/discovery/$", method=["GET"],
          access="read", api=True)
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
        r = [{
            "name": "ping",
            "enable_profile": o.object_profile.enable_ping,
            "status": o.get_status(),
            "last_run": None,
            "last_status": None,
            "next_run": None,
            "jcls": None
        }]

        for name, jcls in self.DISCOVERY_JOBS:
            job = Job.get_job_data(
                "discovery",
                jcls=jcls,
                key=o.id,
                pool=o.pool.name
            ) or {}
            d = {
                "name": name,
                "enable_profile": getattr(o.object_profile,
                                          "enable_%s_discovery" % name),
                "status": job.get(Job.ATTR_STATUS),
                "last_run": self.to_json(job.get(Job.ATTR_LAST)),
                "last_status": job.get(Job.ATTR_LAST_STATUS),
                "next_run": self.to_json(job.get(Job.ATTR_TS)),
                "jcls": jcls
            }
            r += [d]
        return r

    @view(url="^actions/set_managed/$", method=["POST"],
          access="create", api=True,
          validate={
              "ids": ListOfParameter(element=ModelParameter(ManagedObject), convert=True)
    })
    def api_action_set_managed(self, request, ids):
        for o in ids:
            if not o.has_access(request.user):
                continue
            o.is_managed = True
            o.save()
        return "Selected objects set to managed state"

    @view(url="^actions/set_unmanaged/$", method=["POST"],
          access="create", api=True,
          validate={
              "ids": ListOfParameter(element=ModelParameter(ManagedObject), convert=True)
    })
    def api_action_set_unmanaged(self, request, ids):
        for o in ids:
            if not o.has_access(request.user):
                continue
            o.is_managed = False
            o.save()
        return "Selected objects set to unmanaged state"

    @view(url="^(?P<id>\d+)/discovery/run/$", method=["POST"],
          access="change_discovery", api=True)
    def api_run_discovery(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = ujson.loads(request.raw_post_data).get("names", [])
        for name, jcls in self.DISCOVERY_JOBS:
            if name not in r:
                continue
            if not getattr(o.object_profile,
                           "enable_%s_discovery" % name):
                continue  # Disabled by profile
            Job.submit(
                "discovery",
                jcls,
                key=o.id,
                pool=o.pool.name
            )
        return {
            "success": True
        }

    @view(url="^(?P<id>\d+)/discovery/stop/$", method=["POST"],
          access="change_discovery", api=True)
    def api_stop_discovery(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = ujson.loads(request.raw_post_data).get("names", [])
        for name, jcls in self.DISCOVERY_JOBS:
            if name not in r:
                continue
            if not getattr(o.object_profile,
                           "enable_%s_discovery" % name):
                continue  # Disabled by profile
            Job.remove(
                "discovery",
                jcls,
                key=o.id,
                pool=o.pool.name
            )
        return {
            "success": True
        }

    @view(url="^(?P<id>\d+)/interface/$", method=["GET"],
          access="read", api=True)
    def api_interface(self, request, id):
        """
        GET interfaces
        :param managed_object:
        :return:
        """
        def sorted_iname(s):
            return sorted(s, key=lambda x: split_alnum(x["name"]))

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
                o = [ii for ii in link.other(i)
                     if ii.managed_object.id != i.managed_object.id]
                label = "LAG %s: %s" % (o[0].managed_object.name,
                                        ", ".join(ii.name for ii in o))
            else:
                # Broadcast
                label = ", ".join(
                    "%s:%s" % (ii.managed_object.name, ii.name)
                    for ii in link.other(i))
            return {
                "id": str(link.id),
                "label": label
            }

        # Get object
        o = self.get_object_or_404(ManagedObject, id=int(id))
        if not o.has_access(request.user):
            return self.response_forbidden("Permission denied")
        # Physical interfaces
        # @todo: proper ordering
        default_state = ResourceState.get_default()
        style_cache = {}  # profile_id -> css_style
        l1 = [
            {
                "id": str(i.id),
                "name": i.name,
                "description": i.description,
                "status": i.status,
                "mac": i.mac,
                "ifindex": i.ifindex,
                "lag": (i.aggregated_interface.name
                        if i.aggregated_interface else ""),
                "link": get_link(i),
                "profile": str(i.profile.id) if i.profile else None,
                "profile__label": unicode(i.profile) if i.profile else None,
                "enabled_protocols": i.enabled_protocols,
                "project": i.project.id if i.project else None,
                "project__label": unicode(i.project) if i.project else None,
                "state": i.state.id if i.state else default_state.id,
                "state__label": unicode(i.state if i.state else default_state),
                "vc_domain": i.vc_domain.id if i.vc_domain else None,
                "vc_domain__label": unicode(i.vc_domain) if i.vc_domain else None,
                "row_class": get_style(i)
            } for i in Interface.objects.filter(
                managed_object=o.id, type="physical")
        ]
        # LAG
        lag = [
            {
                "id": str(i.id),
                "name": i.name,
                "description": i.description,
                "profile": str(i.profile.id) if i.profile else None,
                "profile__label": unicode(i.profile) if i.profile else None,
                "members": [j.name for j in Interface.objects.filter(
                    managed_object=o.id, aggregated_interface=i.id)],
                "row_class": get_style(i)
            } for i in Interface.objects.filter(managed_object=o.id,
                                                type="aggregated")
        ]
        # L2 interfaces
        l2 = [
            {
                "name": i.name,
                "description": i.description,
                "untagged_vlan": i.untagged_vlan,
                "tagged_vlans": i.tagged_vlans
            } for i in
            SubInterface.objects.filter(managed_object=o.id,
                                        enabled_afi="BRIDGE")
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
                "mac": i.mac
            } for i in SubInterface.objects.filter(managed_object=o.id).filter(q)
        ]
        return {
            "l1": sorted_iname(l1),
            "lag": sorted_iname(lag),
            "l2": sorted_iname(l2),
            "l3": sorted_iname(l3)
        }

    @view(url="^(?P<id>\d+)/interface/$", method=["POST"],
          access="change_interface", api=True)
    def api_set_interface(self, request, id):
        def get_or_none(c, v):
            if not v:
                return None
            return c.objects.get(id=v)
        o = self.get_object_or_404(ManagedObject, id=int(id))
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        d = ujson.loads(request.raw_post_data)
        if "id" in d:
            i = self.get_object_or_404(Interface, id=d["id"])
            if i.managed_object.id != o.id:
                return self.response_not_found()
            # Set profile
            if "profile" in d:
                p = get_or_none(InterfaceProfile, d["profile"])
                i.profile = p
                if p:
                    i.profile_locked = True
            # Project
            if "project" in d:
                i.project = get_or_none(Project, d["project"])
            # State
            if "state" in d:
                i.state = get_or_none(ResourceState, d["state"])
            # VC Domain
            if "vc_domain" in d:
                i.vc_domain = get_or_none(VCDomain, d["vc_domain"])
            #
            i.save()
        return {
            "success": True
        }

    @view(method=["DELETE"], url="^(?P<id>\d+)/?$", access="delete", api=True)
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
            return self.render_json({
                "status": False,
                "message": "Not found"
            }, status=self.NOT_FOUND)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        # Run sa.wipe_managed_object job instead
        o.name = "wiping-%d" % o.id
        o.is_managed = False
        o.description = "Wiping! Do not touch!"
        o.save()
        call_later(
            "noc.sa.wipe.managedobject.wipe",
            o=o.id
        )
        return HttpResponse(status=self.DELETED)

    @view(url="^actions/run_discovery/$", method=["POST"],
          access="launch", api=True,
          validate={
              "ids": ListOfParameter(element=ModelParameter(ManagedObject), convert=True)
    })
    def api_action_run_discovery(self, request, ids):
        d = 0
        for o in ids:
            if not o.has_access(request.user):
                continue
            o.run_discovery(delta=d)
            d += 1
        return "Discovery processes has been scheduled"

    def get_nested_inventory(self, o):
        rev = o.get_data("asset", "revision")
        if rev == "None":
            rev = ""
        r = {
            "id": str(o.id),
            "serial": o.get_data("asset", "serial"),
            "revision": rev or "",
            "description": o.model.description,
            "model": o.model.name
        }
        children = []
        for n in o.model.connections:
            if n.direction == "i":
                c, r_object, _ = o.get_p2p_connection(n.name)
                if c is None:
                    children += [{
                        "id": None,
                        "name": n.name,
                        "leaf": True,
                        "serial": None,
                        "description": "--- EMPTY ---",
                        "model": None
                    }]
                else:
                    cc = self.get_nested_inventory(r_object)
                    cc["name"] = n.name
                    children += [cc]
            elif n.direction == "s":
                children += [{
                    "id": None,
                    "name": n.name,
                    "leaf": True,
                    "serial": None,
                    "description": n.description,
                    "model": ", ".join(n.protocols)
                }]
        if children:
            to_expand = "Transceiver" not in o.model.name
            r["children"] = children
            r["expanded"] = to_expand
        else:
            r["leaf"] = True
        return r

    @view(url="^(?P<id>\d+)/inventory/$", method=["GET"],
          access="read", api=True)
    def api_inventory(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = []
        for p in o.get_inventory():
            c = self.get_nested_inventory(p)
            c["name"] = p.name or o.name
            r += [c]
        return {
            "expanded": True,
            "children": r
        }

    @view(url="^(?P<id>\d+)/job_log/(?P<job>\S+)/$", method=["GET"],
          access="read", api=True)
    def api_job_log(self, request, id, job):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        # fs = gridfs.GridFS(get_db(), "noc.joblog")
        key = "discovery-%s-%s" % (job, o.id)
        d = get_db()["noc.joblog"].find_one({"_id": key})
        if d and d["log"]:
            return self.render_plain_text(
                zlib.decompress(str(d["log"]))
            )
        else:
            return self.render_plain_text("No data")

    @view(url="^(?P<id>\d+)/interactions/$", method=["GET"],
          access="interactions", api=True)
    def api_interactions(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        return [{
            "ts": self.to_json(i.timestamp),
            "op": i.op,
            "user": i.user,
            "text": i.text
        } for i in InteractionLog.objects.filter(object=o.id).order_by("-timestamp")]

    @view(url="^(?P<id>\d+)/scripts/$", method=["GET"], access="script",
          api=True)
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
                "preview": interface.preview or "NOC.sa.managedobject.scripts.JSONPreview"
            }
            r += [ss]
        return r

    @view(url="^(?P<id>\d+)/scripts/(?P<name>[^/]+)/$",
          method=["POST"], access="script", api=True)
    def api_run_script(self, request, id, name):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return {
                "error": "Access denied"
            }
        if name not in o.scripts:
            return {
                "error": "Script not found: %s" % name
            }
        params = self.deserialize(request.raw_post_data)
        try:
            result = o.scripts[name](**params)
        except Exception as e:
            return {
                "error": str(e)
            }
        return {
            "result": result
        }

    @view(url="(?P<id>\d+)/caps/$", method=["GET"],
          access="read", api=True)
    def api_get_caps(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = []
        oc = ObjectCapabilities.objects.filter(object=o).first()
        if oc:
            for c in oc.caps:
                r += [{
                    "capability": c.capability.name,
                    "description": c.capability.description,
                    "type": c.capability.type,
                    "value": c.value,
                    "source": c.source
                }]
        return sorted(r, key=lambda x: x["capability"])

    @view(url="(?P<id>\d+)/facts/$", method=["GET"],
          access="read", api=True)
    def api_get_facts(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        return sorted(
            (
                {
                    "cls": f.cls,
                    "label": f.label,
                    "attrs": [
                        {
                            "name": a,
                            "value": f.attrs[a]
                        } for a in f.attrs
                    ],
                    "introduced": f.introduced.isoformat(),
                    "changed": f.changed.isoformat()
                } for f in ObjectFact.objects.filter(object=o.id)),
            key=lambda x: (x["cls"], x["label"]))

    @view(url="(?P<id>\d+)/revalidate/$", method=["POST"],
          access="read", api=True)
    def api_revalidate(self, request, id):
        def revalidate(o):
            engine = Engine(o)
            engine.check()
            return self.response({"status": True}, self.OK)

        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        return self.submit_slow_op(request, revalidate, o)

    @view(url="(?P<id>\d+)/actions/(?P<action>\S+)/$", method=["POST"],
          access="action", api=True)
    def api_action(self, request, id, action):
        def execute(o, a, args):
            return a.execute(o, **args)

        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        a = self.get_object_or_404(Action, name=action)
        # @todo: Check access
        body = request.raw_post_data
        if body:
            args = ujson.loads(body)
        else:
            args = {}
        return self.submit_slow_op(request, execute, o, a, args)

    @view(url="^link/fix/(?P<link_id>[0-9a-f]{24})/$",
          method=["POST"], access="change_link")
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
            return {
                "status": False,
                "message": message % args
            }

        def success_status(message, *args):
            self.logger.error(message, *args)
            return {
                "status": True,
                "message": message % args
            }

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
            return error_status("[%s] Cannot find %s in the MAC address table",
                                mo1.name, mo2.name)
        # mo2: Find mo1
        i2 = get_interface(r2, mac1)
        if not i1:
            return error_status("[%s] Cannot find %s in the MAC address table",
                                mo2.name, mo1.name)
        self.logger.info("%s:%s -- %s:%s", mo1.name, i1, mo2.name, i2)
        if link.interfaces[0].name == i1 and link.interfaces[1].name == i2:
            return success_status("Linked properly")
        # Get interfaces
        iface1 = mo1.get_interface(i1)
        if not iface1:
            return error_status("[%s] Interface not found: %s",
                                mo1.name, i1)
        iface2 = mo2.get_interface(i2)
        if not iface2:
            return error_status("[%s] Interface not found: %s",
                                mo2.name, i2)
        # Check we can relink
        if_ids = [i.id for i in link.interfaces]
        if iface1.id not in if_ids and iface1.is_linked:
            return error_status(
                "[%s] %s is already linked",
                mo1.name, i1
            )
        if iface2.id not in if_ids and iface2.is_linked:
            return error_status(
                "[%s] %s is already linked",
                mo2.name, i2
            )
        # Relink
        self.logger.info("Relinking")
        link.delete()
        iface1.link_ptp(iface2, method="macfix")
        return success_status("Relinked")
