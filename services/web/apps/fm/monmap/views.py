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


class MonmapApplication(ExtApplication):
    title = _("Monmap")
    menu = _("Monmap")
    glyph = "globe"
    link = "/api/card/view/monmap/1/"
