# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.probe application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.probe import Probe


class ProbeApplication(ExtDocApplication):
    """
    PMProbe application
    """
    title = "Probe"
    menu = "Setup | Probes"
    model = Probe
    query_fields = ["name"]