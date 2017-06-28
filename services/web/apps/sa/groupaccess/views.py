# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.groupaccess application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.sa.models.groupaccess import GroupAccess
from noc.core.translation import ugettext as _


class GroupAccessApplication(ExtModelApplication):
    """
    GroupAccess application
    """
    title = _("Group Access")
    menu = [_("Setup"), _("Group Access")]
    model = GroupAccess
