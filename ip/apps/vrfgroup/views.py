# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.vrfgroup application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.ip.models import VRFGroup


class VRFGroupApplication(ExtModelApplication):
    """
    VRFGroup application
    """
    title = "VRF Groups"
    menu = "Setup | VRF Groups"
    model = VRFGroup
    query_condition = "icontains"

    def field_vrf_count(self, obj):
        return obj.vrf_set.count()
