# ----------------------------------------------------------------------
# vc.vlan application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
from mongoengine import Q

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.subinterface import SubInterface
from noc.vc.models.vlan import VLAN
from noc.vc.models.l2domain import L2Domain
from noc.inv.models.resourcepool import ResourcePool
from noc.lib.app.decorators.state import state_handler
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import (
    DocumentParameter,
)


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

    def bulk_field_interfaces_count(self, data):
        if not data:
            return data

        l2_domains = (d["l2domain"] for d in data)
        objects = L2Domain.get_l2_domain_object_ids(l2_domains)
        vlans = [d["vlan"] for d in data]
        interfaces_count = SubInterface.objects.filter(
            Q(managed_object__in=objects)
            & (
                Q(untagged_vlan__in=vlans, enabled_afi=["BRIDGE"])
                | Q(tagged_vlans__in=vlans, enabled_afi=["BRIDGE"])
                | Q(vlan_ids__in=vlans)
            )
        ).count()
        for row in data:
            row["interfaces_count"] = interfaces_count
        return data

    def bulk_field_prefixes(self, data):
        if not data:
            return data

        for row in data:
            row["prefixes"] = 0
        return data

    @view(url=r"^(?P<vlan_id>[0-9a-f]{24})/interfaces/$", method=["GET"], access="read", api=True)
    def api_interfaces(self, request, vlan_id: int):
        """
        Returns a dict of {untagged: ..., tagged: ...., l3: ...}
        :param request:
        :param vlan_id:
        :return:
        """
        vlan: "VLAN" = self.get_object_or_404(VLAN, id=vlan_id)
        # Managed objects in L2 Domain
        objects = L2Domain.get_l2_domain_object_ids((vlan.l2domain,))
        # Find untagged interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
            managed_object__in=objects, untagged_vlan=vlan.vlan, enabled_afi="BRIDGE"
        ):
            si_objects[si.managed_object] += [{"name": si.name}]
        untagged = [
            {
                "managed_object_id": o.id,
                "managed_object_name": o.name,
                "interfaces": sorted(si_objects[o], key=lambda x: x["name"]),
            }
            for o in si_objects
        ]
        # Find tagged interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
            managed_object__in=objects, tagged_vlans=vlan.vlan, enabled_afi="BRIDGE"
        ):
            si_objects[si.managed_object] += [{"name": si.name}]
        tagged = [
            {
                "managed_object_id": o.id,
                "managed_object_name": o.name,
                "interfaces": sorted(si_objects[o], key=lambda x: x["name"]),
            }
            for o in si_objects
        ]
        # Find l3 interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(managed_object__in=objects, vlan_ids=vlan.vlan):
            si_objects[si.managed_object] += [
                {
                    "name": si.name,
                    "ipv4_addresses": si.ipv4_addresses,
                    "ipv6_addresses": si.ipv6_addresses,
                }
            ]
        l3 = [
            {
                "managed_object_id": o.id,
                "managed_object_name": o.name,
                "interfaces": sorted(si_objects[o], key=lambda x: x["name"]),
            }
            for o in si_objects
        ]
        #
        return {
            "untagged": sorted(untagged, key=lambda x: x["managed_object_name"]),
            "tagged": sorted(tagged, key=lambda x: x["managed_object_name"]),
            "l3": sorted(l3, key=lambda x: x["managed_object_name"]),
        }

    @view(
        url="^find_free/$",
        method=["GET"],
        access="read",
        api=True,
        validate={
            "l2_domain": DocumentParameter(L2Domain),
            "pool": DocumentParameter(ResourcePool, required=False),
        },
    )
    def api_find_free(self, request, l2_domain: "L2Domain", pool: "ResourcePool" = None, **kwargs):
        return l2_domain.get_free_vlan_num(pool=pool)
