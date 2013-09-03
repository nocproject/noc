# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.macdb application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.sa.models import ManagedObject
from noc.inv.models import MACDB, MACLog, Interface, Q

##@todo: REST proxy for backend buffered output(paging support in history)
##@todo: search in field Managed Object/Port/Description

class MACApplication(ExtDocApplication):
    """
    MAC application
    """
    title = "MacDB"
    menu = "Mac DB"
    model = MACDB

    query_fields = ["mac"]
    query_condition = "icontains"
    int_query_fields = ["vlan"]

    implied_permissions = {
        "read": ["inv:macdb:lookup", "main:style:lookup"]
    }

    def field_description(self, o):
        for i in Interface.objects.filter(id=o.interface.id):
            if i.description:
                return i.description
            else:
                return None

    @view(url="^(?P<mac>[0-9A-F:]+)/$", method=["GET"],
        access="view", api=True)
    def api_get_maclog(self, request, mac):
        """
        GET maclog
        :param mac:
        :return:
        """
        current = []
        
        m = MACDB.objects.filter(mac=mac).order_by("-timestamp")
        for p in m:
            if p:
                vc_d = str(p.vc_domain.name) if p.vc_domain else None

                for i in Interface.objects.filter(id=p.interface.id):
                    if i.description:
                        descr = i.description
                    else:
                        descr = None

                current = [{
                    "timestamp": str(p.last_changed),
                    "mac": p.mac,
                    "vc_domain": vc_d,
                    "vlan": p.vlan,
                    "managed_object_name": str(p.managed_object.name),
                    "interface_name": str(p.interface.name),
                    "description": descr
                }]

        history = []
        id_cache = {}
        d_cache = {}

        for i in MACLog.objects.filter(mac=mac).order_by("-timestamp"):
            id = id_cache.get(i.managed_object_name)
            if id is None:        
                for p in ManagedObject.objects.filter(name=i.managed_object_name):
                    id = p.id
                    id_cache[i.managed_object_name] = p.id
            c = d_cache.get((id, i.interface_name))
            if c is None:
                for d in Interface.objects.filter(managed_object=id, name=i.interface_name):
                    if d:
                        if d.description:
                            c = d.description
                            d_cache[id, i.interface_name] = d.description
                        else:
                            c = ""
                            d_cache[id, i.interface_name] = ""
                            
                    else:
                        c = ""
                        d_cache[id, i.interface_name] = ""

            history += [{
                    "timestamp": str(i.timestamp),
                    "mac": i.mac,
                    "vc_domain": str(i.vc_domain_name),
                    "vlan": i.vlan,
                    "managed_object_name": str(i.managed_object_name),
                    "interface_name": str(i.interface_name),
                    "description": c
            }]
        return current + history
