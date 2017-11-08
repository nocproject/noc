# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.totaloutage
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.config import config
from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extapplication import ExtApplication


class TotalOutageApplication(ExtApplication):
    title = _("Total Outages")
    menu = _("Total Outages")
    glyph = "bolt"
    link = "/api/card/view/totaloutage/1/?refresh=%s" % config.fm.total_outage_refresh
