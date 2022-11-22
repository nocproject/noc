# ---------------------------------------------------------------------
# fm.ttsystem application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.fm.models.ttsystem import TTSystem
from noc.core.translation import ugettext as _


class TTSystemApplication(ExtDocApplication):
    """
    TTSystem application
    """

    title = _("TT System")
    menu = [_("Setup"), _("TT System")]
    model = TTSystem
