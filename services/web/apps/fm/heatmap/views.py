# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.totaloutage
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extapplication import ExtApplication


class HeatmapApplication(ExtApplication):
    title = _("Heatmap")
    menu = _("Heatmap")
    glyph = "globe"
    link = "/api/card/view/alarmheat/1/"
