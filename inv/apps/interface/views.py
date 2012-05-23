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


class InterfaceAppplication(ExtApplication):
    """
    inv.interface application
    """
    title = "Interfaces"
    menu = "Interfaces"

    @view(url="^(?P<managed_object>\d+)/$", method=["GET"],
        access="view", api=True)
    def api_get_interfaces(self, request, managed_object):
        """
        GET interfaces
        :param managed_object:
        :return:
        """
        # Get object
        o = self.get_object_or_404(ManagedObject, id=int(managed_object))
        if not o.has_access(request.user):
            return self.response_forbidden("Permission denied")
        # Physical interfaces
        # @todo: proper ordering
        l1 = [
            {
                "name": i.name,
                "description": i.description,
                "mac": i.mac,
                "ifindex": i.ifindex,
                "lag": (i.aggregated_interface.name
                        if i.aggregated_interface else "")
            } for i in
              Interface.objects.filter(managed_object=o.id,
                                       type="physical").order_by("name")
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
                                       type="aggregated").order_by("name")
        ]
        # L3 interfaces
        q = Q(is_ipv4=True) | Q(is_ipv6=True)
        l3 = [
            {
                "name": i.name,
                "description": i.description,
                "ipv4_addresses": i.ipv4_addresses,
                "ipv6_addresses": i.ipv6_addresses,
                "vlan": i.vlan_ids
            } for i in
              SubInterface.objects.filter(managed_object=o.id)\
                .filter(q).order_by("name")
        ]
        return {
            "l1": l1,
            "lag": lag,
            "l3": l3
        }
