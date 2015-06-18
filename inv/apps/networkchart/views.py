# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.networkchart application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.inv.models.networkchart import NetworkChart


class NetworkChartApplication(ExtModelApplication):
    """
    NetworkChart application
    """
    title = "Network Charts"
    menu = "Setup | Network Charts"
    model = NetworkChart
