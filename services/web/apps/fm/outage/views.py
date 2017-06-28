# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.totaloutage
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extapplication import ExtApplication
from noc.core.translation import ugettext as _


class OutageApplication(ExtApplication):
    title = _("Outages")
    menu = _("Outages")
    glyph = "bolt"
    link = "/api/card/view/outage/1/?refresh=60"
