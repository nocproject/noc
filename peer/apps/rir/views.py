# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.rir application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import RIR


class RIRApplication(ExtModelApplication):
    """
    RIR application
    """
    title = "RIR"
    menu = "Setup | RIRs"
    model = RIR
