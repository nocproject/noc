# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# maintainance.maintainancetype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.maintainance.models.maintainancetype import MaintainanceType
from noc.core.translation import ugettext as _


class MaintainanceTypeApplication(ExtDocApplication):
    """
    MaintainanceType application
    """
    title = _("Maintainance Type")
    menu = [_("Setup"), _("Maintainance Types")]
    model = MaintainanceType
