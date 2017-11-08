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


class CardApplication(ExtApplication):
    title = _("Cards")
    menu = _("Cards")
    glyph = "book"
    link = "/api/card/index.html"
