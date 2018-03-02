# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.crontab application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.crontab import CronTab
from noc.core.translation import ugettext as _


class CronTabApplication(ExtDocApplication):
    """
    CronTab application
    """
    title = "CronTab"
    menu = [_("Setup"), _("CronTabs")]
    model = CronTab
    glyph = "calendar"

    def field_crontab_expression(self, o):
        return o.crontab_expression
