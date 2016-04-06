# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## maintainance.maintainancetype application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.maintainance.models.maintainancetype import MaintainanceType


class MaintainanceTypeApplication(ExtDocApplication):
    """
    MaintainanceType application
    """
    title = "Maintainance Type"
    menu = "Setup | Maintainance Types"
    model = MaintainanceType
