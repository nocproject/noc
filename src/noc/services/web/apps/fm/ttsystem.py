# ---------------------------------------------------------------------
# fm.ttsystem application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.fm.models.ttsystem import TTSystem
from noc.services.web.base.extdocapplication import ExtDocApplication


class TTSystemApplication(ExtDocApplication):
    """
    TTSystem application
    """

    title = _("TT System")
    menu = [_("Setup"), _("TT System")]
    model = TTSystem
