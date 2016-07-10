# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.area application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.gis.models import Area


class AreaApplication(ExtDocApplication):
    """
    Area application
    """
    title = "Area"
    menu = "Setup | Areas"
    model = Area
