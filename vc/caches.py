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


# Instances
vcinterfacescount = VCInterfacesCount()
