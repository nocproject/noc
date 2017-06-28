# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.dbtrigger application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.main.models.dbtrigger import DBTrigger
from noc.core.translation import ugettext as _


class DBTriggerApplication(ExtModelApplication):
    """
    DBTrigger application
    """
    title = _("DB Triggers")
    menu = [_("Setup"), _("DB Triggers")]
    model = DBTrigger
    icon = "icon_database_gear"
