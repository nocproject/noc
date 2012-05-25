# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.interface application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.models import ManagedObject
from noc.inv.models import Interface, SubInterface, Q
from noc.sa.interfaces import StringParameter, ListOfParameter,\
    DocumentParameter
from noc.lib.text import split_alnum


class InterfaceAppplication(ExtApplication):
    """
    inv.interface application
    """
    title = "Interfaces"
    menu = "Interfaces"

    mrt_config = {
        "get_mac": {
            "map_script": "get_mac_address_table",
            "timeout": 120,
            "access": "get_mac"
        }
    }

    @view(url="^(?P<managed_object>\d+)/$", method=["GET"],
        access="view", api=True)
    def api_get_interfaces(self, request, managed_object):
        """
        GET interfaces
        :param managed_object:
        :return:
        """
        def sorted_iname(s):
            return sorted(s, key=lambda x: split_alnum(x["name"]))

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
                     if ii.managed_object.id != i.managed_object_id]
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
        o = self.get_object_or_404(ManagedObject, id=int(managed_object))
        if not o.has_access(request.user):
            return self.response_forbidden("Permission denied")
        # Physical interfaces
        # @todo: proper ordering
        l1 = [
            {
                "id": str(i.id),
                "name": i.name,
                "description": i.description,
                "mac": i.mac,
                "ifindex": i.ifindex,
                "lag": (i.aggregated_interface.name
                        if i.aggregated_interface else ""),
                "link": get_link(i)
            } for i in
              Interface.objects.filter(managed_object=o.id,
                                       type="physical")
        ]
        # LAG
        lag = [
            {
                "name": i.name,
                "description": i.description,
                "members": [j.name for j in Interface.objects.filter(
                    managed_object=o.id, aggregated_interface=i.id)]
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
                  is_bridge=True)
        ]
        # L3 interfaces
        q = Q(is_ipv4=True) | Q(is_ipv6=True)
        l3 = [
            {
                "name": i.name,
                "description": i.description,
                "ipv4_addresses": i.ipv4_addresses,
                "ipv6_addresses": i.ipv6_addresses,
                "vlan": i.vlan_ids,
                "vrf": i.forwarding_instance.name if i.forwarding_instance else ""
            } for i in
              SubInterface.objects.filter(managed_object=o.id)\
                .filter(q)
        ]
        return {
            "l1": sorted_iname(l1),
            "lag": sorted_iname(lag),
            "l2": sorted_iname(l2),
            "l3": sorted_iname(l3)
        }

    @view(url="^link/$", method=["POST"],
        validate={
            "type": StringParameter(choices=["ptp"]),
            "interfaces": ListOfParameter(element=DocumentParameter(Interface))
        },
        access="link", api=True)
    def api_link(self, request, type, interfaces):
        if type == "ptp":
            if len(interfaces) == 2:
                interfaces[0].link_ptp(interfaces[1])
                return {
                    "status": True
                }
            else:
                raise ValueError, "Invalid interfaces length"
        return {
            "status": False
        }

    @view(url="^unlink/(?P<iface_id>[0-9a-f]{24})/$", method=["POST"],
        access="link", api=True)
    def api_unlink(self, request, iface_id):
        i = Interface.objects.filter(id=iface_id).first()
        if not i:
            return self.response_not_found()
        try:
            i.unlink()
            return {
                "status": True,
                "msg": "Unlinked"
            }
        except ValueError, why:
            return {
                "status": False,
                "msg": str(why)
            }

    @view(url="^unlinked/(?P<object_id>\d+)/$", method=["GET"],
        access="link", api=True)
    def api_unlinked(self, request, object_id):
        o = self.get_object_or_404(ManagedObject, id=int(object_id))
        r = [{"id": str(i.id), "label": i.name}
            for i in Interface.objects.filter(managed_object=o.id,
                                        type="physical").order_by("name")
            if not i.link]
        return sorted(r, key=lambda x: split_alnum(x["label"]))
