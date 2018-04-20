# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.monitor application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view


class MonitorApplication(ExtApplication):
    """
    sa.monitor application
    """
    title = "Monitor"
    menu = "Monitor"
    icon = "icon_monitor"

    mrt_config = {
        "get_activator_info": {
            "map_script": "get_activator_info",
            "timeout": 10,
            "access": "launch"
        }
    }
