# ---------------------------------------------------------------------
# fm.totaloutage
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.services.web.base.extapplication import ExtApplication


class MonmapApplication(ExtApplication):
    title = _("Monmap")
    menu = _("Monmap")
    glyph = "globe"
    link = "/api/card/view/monmap/1/"
