# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.monitor application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _


class MonitorApplication(ExtApplication):
    """
    sa.monitor application
    """
    title = _("Monitor")
    menu = _("Monitor")
    icon = "icon_monitor"

    mrt_config = {
        "get_activator_info": {
            "map_script": "get_activator_info",
            "timeout": 10,
            "access": "launch"
        }
    }
