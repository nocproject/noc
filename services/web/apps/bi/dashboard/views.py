# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.card
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extapplication import ExtApplication


class BIDashboardApplication(ExtApplication):
    title = _("Dashboard")
    menu = _("Dashboard")
    glyph = "dashboard"
    link = "/api/bi/index.html"
