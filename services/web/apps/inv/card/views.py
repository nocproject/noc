# ---------------------------------------------------------------------
# inv.card
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extapplication import ExtApplication
from noc.core.translation import ugettext as _


class CardApplication(ExtApplication):
    title = _("Cards")
    menu = _("Cards")
    glyph = "book"
    link = "/api/card/index.html"
