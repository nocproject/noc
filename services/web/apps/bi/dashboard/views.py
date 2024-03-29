# ---------------------------------------------------------------------
# inv.card
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extapplication import ExtApplication
from noc.core.translation import ugettext as _


class BIDashboardApplication(ExtApplication):
    title = _("Dashboard")
    menu = _("Dashboard")
    glyph = "dashboard"
    link = "/ui/bi2/"
