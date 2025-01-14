# ----------------------------------------------------------------------
# vc.vlan application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Optional, Dict

# Third-party modules
from django.http import HttpResponse
from mongoengine import Q

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.services.web.base.decorators.state import state_handler
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.resourcepool import ResourcePool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.base import DocumentParameter, IntParameter, StringParameter
from noc.vc.models.vlan import VLAN
from noc.vc.models.l2domain import L2Domain
from noc.core.ip import IP
from noc.core.translation import ugettext as _
from noc.core.cache.decorator import cachedmethod


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

    @cachedmethod(key="vlans-interface-count-%s", ttl=180)
    def get_l2domain_interfaces_count(self, l2_domain: str) -> Dict[int, int]:
        """
        Calculate VLAN Count by interface on ManagedObject list
        :param l2_domain:
        :return:
        """
        mos = L2Domain.get_l2_domain_object_ids(l2_domain)
        coll = SubInterface._get_collection()
        r = {}
        for rec in coll.aggregate(
            [
                {"$match": {"managed_object": {"$in": mos}}},
                {
                    "$project": {
                        "uvlans": ["$untagged_vlan"],
                        "tvlans": "$tagged_vlans",
                        "vlan_ids": 1,
                    }
                },
                {"$project": {"vlans": {"$setUnion": ["$uvlans", "$tvlans", "$vlan_ids"]}}},
                {"$unwind": "$vlans"},
                {"$group": {"_id": "$vlans", "count": {"$sum": 1}}},
            ]
        ):
            if not rec["_id"]:
                continue
            r[rec["_id"]] = rec["count"]
        return r

    def bulk_field_interfaces_count(self, data):
        if not data:
            return data
        l2_domains = tuple(d["l2_domain"] for d in data if "l2_domain" in d)
        if not l2_domains:
            return data
        objects = defaultdict(list)
        # @todo group by for speedup
        for mo_id, l2_domain in ManagedObject.objects.filter(l2_domain__in=l2_domains).values_list(
            "id", "l2_domain"
        ):
            objects[l2_domain].append(mo_id)
        interfaces_count = {}
        for l2_domain in objects:
            r = self.get_l2domain_interfaces_count(l2_domain)
            for vlan in r:
                interfaces_count[(l2_domain, vlan)] = r[vlan]
        for row in data:
            row["interfaces_count"] = interfaces_count.get((row["l2_domain"], row["vlan"]), 0)
        return data

    def bulk_field_prefixes(self, data):
        if not data:
            return data
        l2_domains = tuple(d["l2_domain"] for d in data if "l2_domain" in d)
        if not l2_domains:
            return data
        objects = dict(
            mo
            for mo in ManagedObject.objects.filter(l2_domain__in=l2_domains).values_list(
                "id", "l2_domain"
            )
        )

        vlans = [d["vlan"] for d in data]

        prefixes = defaultdict(set)

        # @todo: Exact match on vlan_ids
        for si in SubInterface.objects.filter(
            Q(managed_object__in=list(objects))
            & Q(vlan_ids__in=vlans)
            & (Q(enabled_afi=["IPv4"]) | Q(enabled_afi=["IPv6"]))
        ).only("managed_object", "enabled_afi", "ipv4_addresses", "ipv6_addresses", "vlan_ids"):
            if "IPv4" in si.enabled_afi:
                prefixes[(objects[si["managed_object"].id], si["vlan_ids"][0])].update(
                    {IP.prefix(ip).first for ip in si.ipv4_addresses}
                )
            if "IPv6" in si.enabled_afi:
                prefixes[(objects[si["managed_object"].id], si["vlan_ids"][0])].update(
                    {IP.prefix(ip).first for ip in si.ipv6_addresses}
                )

        for row in data:
            row["prefixes"] = [
                str(x.first) for x in sorted(prefixes.get((row["l2_domain"], row["vlan"]), []))
            ]
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
        objects = L2Domain.get_l2_domain_object_ids(vlan.l2_domain.id)
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
        url="^allocate/$",
        method=["GET"],
        access="allocate",
        api=True,
        validate={
            "l2_domain": DocumentParameter(L2Domain),
            "pool": DocumentParameter(ResourcePool, required=True),
            "vlan_id": IntParameter(required=False, min_value=1, max_value=4096),
            "name": StringParameter(required=False),
        },
    )
    def api_allocate_vlan(
        self,
        request,
        l2_domain: "L2Domain",
        pool: "ResourcePool" = None,
        vlan_id: Optional[int] = None,
        name: Optional[str] = None,
        **kwargs,
    ):
        # @todo check user permission
        with ResourcePool.acquire([pool]):
            allocator = pool.get_allocator(l2_domain=l2_domain, vlan_id=vlan_id)
            r = allocator(
                domain=l2_domain,
                resource_keys=[vlan_id] if vlan_id else None,
                user=request.user,
            )
        if not r:
            return HttpResponse("No Free VLAN found for Allocated", status=self.NOT_FOUND)
        r = r[0]
        if name:
            r.name = name
            r.save()
        return self.instance_to_dict(r)
