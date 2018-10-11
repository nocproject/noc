# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VLAN card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import defaultdict
# NOC modules
from .base import BaseCard
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.subinterface import SubInterface
from noc.vc.models.vlan import VLAN


class VLANCard(BaseCard):
    name = "vlan"
    default_template_name = "vlan"
    model = VLAN

    def get_object(self, id):
        if self.current_user.is_superuser:
            return VLAN.get_by_id(id)
        else:
            return VLAN.objects.get(
                id=id,
                segment__in=self.get_user_domains()
            )

    def get_data(self):
        return {
            "object": self.object,
            "interfaces": self.get_interfaces()
        }

    def get_interfaces(self):
        # Managed objects in VC domain
        objects = NetworkSegment.get_vlan_domain_object_ids(
            self.object.segment)
        # Find untagged interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
                managed_object__in=objects,
                untagged_vlan=self.object.vlan,
                enabled_afi="BRIDGE"):
            si_objects[si.managed_object] += [{"name": si.name}]
        untagged = [{
            "managed_object": o,
            "interfaces": sorted(si_objects[o], key=lambda x: x["name"])
        } for o in si_objects]
        # Find tagged interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
                managed_object__in=objects,
                tagged_vlans=self.object.vlan,
                enabled_afi="BRIDGE"):
            si_objects[si.managed_object] += [{"name": si.name}]
        tagged = [{
            "managed_object": o,
            "interfaces": sorted(si_objects[o], key=lambda x: x["name"])
        } for o in si_objects]
        # Find l3 interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
                managed_object__in=objects,
                vlan_ids=self.object.vlan):
            si_objects[si.managed_object] += [{
                "name": si.name,
                "ipv4_addresses": si.ipv4_addresses,
                "ipv6_addresses": si.ipv6_addresses
            }]
        l3 = [{"managed_object": o,
               "interfaces": sorted(si_objects[o],
                                    key=lambda x: x["name"])
               } for o in si_objects]
        #
        return {
            "has_interfaces": bool(len(untagged) + len(tagged) + len(l3)),
            "untagged": sorted(untagged,
                               key=lambda x: x["managed_object"].name),
            "tagged": sorted(tagged,
                             key=lambda x: x["managed_object"].name),
            "l3": sorted(l3, key=lambda x: x["managed_object"].name)
        }
