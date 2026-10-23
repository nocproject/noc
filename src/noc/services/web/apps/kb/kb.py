# ---------------------------------------------------------------------
# kb.card
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extapplication import ExtApplication
from noc.core.translation import ugettext as _


class KBApplication(ExtApplication):
    title = _("Knowledge Base")
    menu = _("Knowledge Base")
    glyph = "dashboard"
    link = "/api/card/view/kb/0/"
