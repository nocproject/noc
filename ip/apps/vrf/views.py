# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.vrf application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.ip.models import VRF


class VRFApplication(ExtModelApplication):
    """
    VRF application
    """
    title = "VRFs"
    menu = "VRFs"
    model = VRF
    query_fields = ["name", "rd", "description"]
