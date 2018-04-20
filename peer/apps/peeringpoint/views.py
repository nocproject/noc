# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.peeringpoint application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import PeeringPoint

class PeeringPointApplication(ExtModelApplication):
    """
    Peering Point application
    """
    title = "Peering Points"
    menu = "Setup | Peering Points"
    model = PeeringPoint
    query_fields = ["hostname__icontains", "router_id__icontains"]

