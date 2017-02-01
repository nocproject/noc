# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## maintainance.maintainance application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.maintainance.models.maintainance import Maintainance
from noc.core.translation import ugettext as _


class MaintainanceApplication(ExtDocApplication):
    """
    Maintainance application
    """
    title = _("Maintainance")
    menu = _("Maintainance")
    model = Maintainance
    query_condition = "icontains"
    query_fields = ["subject"]
