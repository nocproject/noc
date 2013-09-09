# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.managedobject application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models import ManagedObject, ManagedObjectAttribute
from noc.inv.models.link import Link
from noc.inv.models.interface import Interface
from noc.inv.models.pendinglinkcheck import PendingLinkCheck
from noc.lib.app.modelinline import ModelInline
from noc.lib.app.repoinline import RepoInline
from mongoengine.queryset import Q as MQ
from noc.lib.serialize import json_decode


class ManagedObjectApplication(ExtModelApplication):
    """
    ManagedObject application
    """
    title = "Managed Objects"
    menu = "Managed Objects"
    model = ManagedObject
    query_condition = "icontains"
    # Inlines
    attrs = ModelInline(ManagedObjectAttribute)
    cfg = RepoInline("config")

    def field_platform(self, o):
        return o.platform

    def field_row_class(self, o):
        return o.object_profile.style.css_class_name if o.object_profile.style else ""

    @view(url="^(?P<id>\d+)/links/$", method=["GET"],
          access="read", api=True)
    def api_links(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
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
          access="link", api=True)
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
          access="link", api=True)
    def api_link_reject(self, request):
        d = json_decode(request.raw_post_data)
        plc = self.get_object_or_404(PendingLinkCheck, id=d.get("link"))
        plc.delete()
        return {
            "success": True
        }
