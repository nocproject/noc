# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## maintainance.maintainance application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.maintainance.models.maintainance import Maintainance


class MaintainanceApplication(ExtDocApplication):
    """
    Maintainance application
    """
    title = "Maintainance"
    menu = "Maintainance"
    model = Maintainance
