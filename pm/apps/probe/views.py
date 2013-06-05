# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.probe application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models import PMProbe


class PMProbeApplication(ExtDocApplication):
    """
    PMProbe application
    """
    title = "PM Probe"
    menu = "Setup | PM Probes"
    model = PMProbe
    query_fields = ["name"]