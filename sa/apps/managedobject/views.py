# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.managedobject application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
from ConfigParser import SafeConfigParser
import os
import datetime
## Django modules
from django.http import HttpResponse
## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models.managedobject import (ManagedObject,
                                         ManagedObjectAttribute)
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.reducetask import ReduceTask
from noc.sa.models.interactionlog import InteractionLog
from noc.inv.models.link import Link
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.pendinglinkcheck import PendingLinkCheck
from noc.lib.app.modelinline import ModelInline
from noc.lib.app.repoinline import RepoInline
from noc.main.models.resourcestate import ResourceState
from noc.project.models.project import Project
from noc.vc.models.vcdomain import VCDomain
from sa.models.objectcapabilities import ObjectCapabilities
from mongoengine.queryset import Q as MQ
from noc.lib.serialize import json_decode
from noc.lib.scheduler.utils import (get_job, refresh_schedule,
                                     submit_job, stop_schedule,
                                     start_schedule)
from noc.lib.text import split_alnum
from noc.sa.interfaces.base import ListOfParameter, ModelParameter
from noc.inv.discovery.utils import get_active_discovery_methods
from noc.cm.models.objectfact import ObjectFact
from noc.cm.engine import Engine
from noc.sa.models.action import Action


class ManagedObjectApplication(ExtModelApplication):
    """
    ManagedObject application
    """
    title = "Managed Objects"
    menu = "Managed Objects"
    model = ManagedObject
    query_condition = "icontains"
    query_fields = ["name", "description", "address"]
    # Inlines
    attrs = ModelInline(ManagedObjectAttribute)
    cfg = RepoInline("config")

    extra_permissions = ["alarm", "change_interface"]

    mrt_config = {
        "console": {
            "access": "console",
            "map_script": "commands",
            "timeout": 60
        }
    }

    def field_platform(self, o):
        return o.platform

    def field_row_class(self, o):
        return o.object_profile.style.css_class_name if o.object_profile.style else ""

    def field_interface_count(self, o):
        return Interface.objects.filter(managed_object=o.id, type="physical").count()

    def field_link_count(self, o):
        return Link.object_links_count(o)

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
            l = []
            r = []
            for i in link.interfaces:
                if i.managed_object.id == o.id:
                    l += [i]
                else:
                    r += [i]
                for li, ri in zip(l, r):
                    result += [{
                        "id": str(link.id),
                        "local_interface": str(li.id),
                        "local_interface__label": li.name,
                        "remote_object": ri.managed_object.id,
                        "remote_object__label": ri.managed_object.name,
                        "remote_interface": str(ri.id),
                        "remote_interface__label": ri.name,
                        "discovery_method": link.discovery_method,
                        "commited": True,
                        "local_description": li.description,
                        "remote_description": ri.description
                    }]
        # Get pending links
        q = MQ(local_object=o.id) | MQ(remote_object=o.id)
        for link in PendingLinkCheck.objects.filter(q):
            if link.local_object.id == o.id:
                ro = link.remote_object
                lin = link.local_interface
                rin = link.remote_interface
            else:
                ro = link.local_object
                lin = link.remote_interface
                rin = link.local_interface
            li = Interface.objects.filter(managed_object=o.id, name=lin).first()
            if not li:
                continue
            ri = Interface.objects.filter(managed_object=ro.id, name=rin).first()
            if not ri:
                continue
            result += [{
                "id": str(link.id),
                "local_interface": str(li.id),
                "local_interface__label": li.name,
                "remote_object": ro.id,
                "remote_object__label": ro.name,
                "remote_interface": str(ri.id),
                "remote_interface__label": ri.name,
                "discovery_method": link.method,
                "commited": False,
                "local_description": li.description,
                "remote_description": ri.description
            }]
        return result

    @view(url="^link/approve/$", method=["POST"],
          access="change_link", api=True)
    def api_link_approve(self, request):
        d = json_decode(request.raw_post_data)
        plc = self.get_object_or_404(PendingLinkCheck, id=d.get("link"))
        li = Interface.objects.filter(
            managed_object=plc.local_object.id,
            name=plc.local_interface
            ).first()
        if not li:
            return {
                "success": False,
                "error": "Interface not found: %s:%s" % (
                    plc.local_object.name, plc.local_interface)
            }
        ri = Interface.objects.filter(
            managed_object=plc.remote_object.id,
            name=plc.remote_interface
            ).first()
        if not ri:
            return {
                "success": False,
                "error": "Interface not found: %s:%s" % (
                    plc.remote_object.name, plc.remote_interface)
            }
        li.link_ptp(ri, method=plc.method + "+manual")
        plc.delete()
        return {
            "success": True
        }

    @view(url="^link/reject/$", method=["POST"],
          access="change_link", api=True)
    def api_link_reject(self, request):
        d = json_decode(request.raw_post_data)
        plc = self.get_object_or_404(PendingLinkCheck, id=d.get("link"))
        plc.delete()
        return {
            "success": True
        }

    def check_mrt_access(self, request, name):
        # @todo: Check object's access
        return super(ManagedObjectApplication, self).check_mrt_access(request, name)

    @view(url="^(?P<id>\d+)/discovery/$", method=["GET"],
          access="read", api=True)
    def api_discovery(self, request, id):
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
            "link_count": None
        }]
        for name in get_active_discovery_methods():
            job = get_job("inv.discovery", name, o.id) or {}
            if name.endswith("_discovery"):
                lcmethod = name[:-10]
            else:
                lcmethod = None
            d = {
                "name": name,
                "enable_profile": getattr(o.object_profile,
                                          "enable_%s" % name),
                "status": job.get("s"),
                "last_run": self.to_json(job.get("last")),
                "last_status": job.get("ls"),
                "next_run": self.to_json(job.get("ts")),
                "link_count": link_count.get(lcmethod, "")
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
        r = json_decode(request.raw_post_data).get("names", [])
        d = 0
        for name in get_active_discovery_methods():
            cfg = "enable_%s" % name
            if getattr(o.object_profile, cfg) and name in r:
                start_schedule("inv.discovery", name, o.id)
                refresh_schedule("inv.discovery",
                                 name, o.id, delta=d)
                d += 1
        return {
            "success": True
        }

    @view(url="^(?P<id>\d+)/discovery/stop/$", method=["POST"],
          access="change_discovery", api=True)
    def api_stop_discovery(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        r = json_decode(request.raw_post_data).get("names", [])
        d = 0
        for name in get_active_discovery_methods():
            cfg = "enable_%s" % name
            if getattr(o.object_profile, cfg) and name in r:
                stop_schedule("inv.discovery", name, o.id)
                d += 1
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
        style_cache = {}  ## profile_id -> css_style
        l1 = [
            {
                "id": str(i.id),
                "name": i.name,
                "description": i.description,
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
            } for i in
              Interface.objects.filter(managed_object=o.id,
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
            } for i in
              SubInterface.objects.filter(managed_object=o.id).filter(q)
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
        d = json_decode(request.raw_post_data)
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
        submit_job("main.jobs", "sa.wipe_managedobject", key=o.id)
        return HttpResponse(status=self.DELETED)

    @view(url="^actions/run_discovery/$", method=["POST"],
          access="launch", api=True,
          validate={
              "ids": ListOfParameter(element=ModelParameter(ManagedObject), convert=True)
          })
    def api_action_run_discovery(self, request, ids):
        for o in ids:
            if not o.has_access(request.user):
                continue
            d = 0
            for name in get_active_discovery_methods():
                cfg = "enable_%s" % name
                if getattr(o.object_profile, cfg):
                    refresh_schedule(
                        "inv.discovery",
                        name, o.id, delta=d)
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

    @view(url="^(?P<id>\d+)/job_log/(?P<job>[a-zA-Z0-9_]+)/$", method=["GET"],
        access="read", api=True)
    def api_job_log(self, request, id, job):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        if not hasattr(self, "discovery_log_jobs"):
            # Read config
            self.discovery_log_jobs = None
            config = SafeConfigParser()
            config.read("etc/noc-discovery.conf")
            if config.has_section("main") and config.has_option("main", "log_jobs"):
                p = config.get("main", "log_jobs")
                if os.path.isdir(p):
                    self.discovery_log_jobs = p
        if self.discovery_log_jobs:
            p = os.path.join(self.discovery_log_jobs, job, id)
            if os.path.exists(p):
                with open(p) as f:
                    return self.render_plain_text(f.read())
        return self.render_plain_text("No data!")

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
        for s in sorted(o.profile.scripts):
            script = o.profile.scripts[s]
            interface = script.implements[0]
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
            return self.response_forbidden("Access denied")
        if name not in o.profile.scripts:
            return self.response_not_found("Script not found: %s" % name)
        task = ReduceTask.create_task(
            o, "pyrule:mrt_result", {},
            name, {},
            None)
        return task.id

    @view(url="^(?P<id>\d+)/scripts/(?P<name>[^/]+)/(?P<task>\d+)/$",
          method=["GET"], access="script", api=True)
    def api_get_script_result(self, request, id, name, task):
        o = self.get_object_or_404(ManagedObject, id=id)
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        if name not in o.profile.scripts:
            return self.response_not_found("Script not found: %s" % name)
        t = self.get_object_or_404(ReduceTask, id=int(task))
        try:
            r = t.get_result(block=False)
        except ReduceTask.NotReady:
            # Not ready
            return {
                "ready": False,
                "max_timeout": (t.stop_time - datetime.datetime.now()).seconds,
                "result": None
            }
        # Return result
        return {
            "ready": True,
            "max_timeout": 0,
            "result": r[0]
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
                    "discovered_value": c.discovered_value,
                    "local_value": c.local_value,
                    "value": c.local_value if c.local_value is not None else c.discovered_value
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
            args = json_decode(body)
        else:
            args = {}
        return self.submit_slow_op(request, execute, o, a, args)
