# ---------------------------------------------------------------------
# fm.totaloutage
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.translation import ugettext as _
from noc.services.web.base.extapplication import ExtApplication


class OutageApplication(ExtApplication):
    title = _("Outages")
    menu = _("Outages")
    glyph = "bolt"
    link = f"/api/card/view/outage/1/?refresh={config.fm.outage_refresh}"
