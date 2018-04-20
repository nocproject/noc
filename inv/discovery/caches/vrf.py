## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VRF Cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.ip.models.vrf import VRF


class VRFCache(object):
    def __init__(self):
        self.cache_vrf_by_rd = {}
        self.cache_vrf_by_name = {}

    def info(self, object, msg):
        logging.info("[VRF Cache] %s: %s" % (object.name, msg))

    def get_or_create(self, object, name, rd):
        """
        :param object:
        :param name:
        :param rd:
        :return:
        """
        def set_cache(vrf):
            self.cache_vrf_by_rd[vrf.rd] = vrf
            self.cache_vrf_by_name[vrf.name] = vrf
            return vrf

        if name == "default":
            if object.vrf:
                # Use object's VRF is set
                return object.vrf
            # Get default VRF
            try:
                return self.cache_vrf_by_name["default"]
            except KeyError:
                return set_cache(VRF.get_global())
        # Non-default VRF
        if not rd:
            rd = VRF.generate_rd(name)
        # Lookup RD cache
        try:
            return self.cache_vrf_by_rd[rd]
        except KeyError:
            pass
        # Lookup database
        try:
            return set_cache(VRF.objects.get(rd=rd))
        except VRF.DoesNotExist:
            pass
        # VRF Not found, create
        # Generate unique VRF in case of names clash
        vrf_name = name
        if VRF.objects.filter(name=vrf_name).exists():
            # Name clash, generate new name by appending RD
            vrf_name += "_%s" % rd
            self.info(object,
                "Conflicting names for VRF %s. Using fallback name %s" % (name, vrf_name))
        # Create VRF
        vrf = VRF(name=vrf_name,
            rd=rd,
            vrf_group=VRF.get_global().vrf_group
        )
        vrf.save()
        return set_cache(vrf)

##
## Global VRF Cache instance
##
vrf_cache = VRFCache()
