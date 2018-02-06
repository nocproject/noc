# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.vlan application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.subinterface import SubInterface
from noc.vc.models.vlan import VLAN
from noc.lib.app.decorators.state import state_handler
from noc.core.translation import ugettext as _


@state_handler
class VLANApplication(ExtDocApplication):
    """
    VLAN application
    """
    title = "VLAN"
    menu = [_("VLAN")]
    model = VLAN
    query_fields = ["name", "description"]
    query_condition = "icontains"
    int_query_fields = ["vlan"]

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    def clean_list_data(self, data):
        return data

    @view(url=r"^(?P<vlan_id>[0-9a-f]{24})/interfaces/$", method=["GET"],
          access="read", api=True)
    def api_interfaces(self, request, vlan_id):
        """
        Returns a dict of {untagged: ..., tagged: ...., l3: ...}
        :param request:
        :param vlan_id:
        :return:
        """
        vlan = self.get_object_or_404(VLAN, id=vlan_id)
        # Managed objects in VC domain
        objects = NetworkSegment.get_vlan_domain_object_ids(
            vlan.segment)
        # Find untagged interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
                managed_object__in=objects,
                untagged_vlan=vlan.vlan,
                enabled_afi="BRIDGE"):
            si_objects[si.managed_object] += [{"name": si.name}]
        untagged = [{
            "managed_object_id": o.id,
            "managed_object_name": o.name,
            "interfaces": sorted(si_objects[o], key=lambda x: x["name"])
        } for o in si_objects]
        # Find tagged interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
                managed_object__in=objects,
                tagged_vlans=vlan.vlan,
                enabled_afi="BRIDGE"):
            si_objects[si.managed_object] += [{"name": si.name}]
        tagged = [{
            "managed_object_id": o.id,
            "managed_object_name": o.name,
            "interfaces": sorted(si_objects[o], key=lambda x: x["name"])
        } for o in si_objects]
        # Find l3 interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
                managed_object__in=objects,
                vlan_ids=vlan.vlan):
            si_objects[si.managed_object] += [{
                "name": si.name,
                "ipv4_addresses": si.ipv4_addresses,
                "ipv6_addresses": si.ipv6_addresses
            }]
        l3 = [{"managed_object_id": o.id,
               "managed_object_name": o.name,
               "interfaces": sorted(si_objects[o],
                                    key=lambda x: x["name"])
               } for o in si_objects]
        #
        return {
            "untagged": sorted(untagged,
                               key=lambda x: x["managed_object_name"]),
            "tagged": sorted(tagged,
                             key=lambda x: x["managed_object_name"]),
            "l3": sorted(l3, key=lambda x: x["managed_object_name"])
        }
