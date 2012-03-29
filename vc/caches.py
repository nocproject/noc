# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's standard models module
## For VC application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.settings import config
from noc.lib.cache import Cache
from noc.inv.models import SubInterface, Q
from noc.vc.models import VC
from noc.sa.caches import managedobjectselector_object_ids
from noc.lib.ip import IP


class VCInterfacesCount(Cache):
    cache_id = "vc_vcinterfacescount"
    ttl = config.getint("cache", "vc_vcinterfacescount")

    @classmethod
    def get_key(cls, vc):
        if hasattr(vc, "id"):
            return vc.id
        else:
            return int(vc)

    @classmethod
    def find(cls, vc):
        if not hasattr(vc, "id"):
            vc = VC.objects.get(id=int(vc))
        if not vc.vc_domain.selector:
            return 0
        objects = managedobjectselector_object_ids.get(vc.vc_domain.selector)
        l1 = vc.l1
        n = SubInterface.objects.filter(
            Q(managed_object__in=objects) &
            (
                Q(untagged_vlan=l1, is_bridge=True) |
                Q(tagged_vlans=l1, is_bridge=True) |
                Q(vlan_ids=l1)
            )
        ).count()
        return n


class VCPrefixes(Cache):
    cache_id = "vc_vcprefixes"
    ttl = config.getint("cache", "vc_vcprefixes")
    @classmethod
    def get_key(cls, vc):
        if hasattr(vc, "id"):
            return vc.id
        else:
            return int(vc)

    @classmethod
    def find(cls, vc):
        if not hasattr(vc, "id"):
            vc = VC.objects.get(id=int(vc))
        if not vc.vc_domain.selector:
            return []
        objects = managedobjectselector_object_ids.get(vc.vc_domain.selector)
        ipv4 = set()
        ipv6 = set()
        # @todo: Exact match on vlan_ids
        for si in SubInterface.objects.filter(
            Q(managed_object__in=objects) &
            Q(vlan_ids=vc.l1) &
            (Q(is_ipv4=True) | Q(is_ipv6=True))
        ).only("is_ipv4", "is_ipv6", "ipv4_addresses", "ipv6_addresses"):
            if si.is_ipv4:
                ipv4.update([IP.prefix(ip).first
                          for ip in si.ipv4_addresses])
            if si.is_ipv6:
                ipv6.update([IP.prefix(ip).first
                          for ip in si.ipv6_addresses])
        p = [str(x.first) for x in sorted(ipv4)]
        p += [str(x.first) for x in sorted(ipv6)]
        return p


# Instances
vcinterfacescount = VCInterfacesCount()
vcprefixes = VCPrefixes()
