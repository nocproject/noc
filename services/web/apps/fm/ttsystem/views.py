# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.ttsystem application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.fm.models.ttsystem import TTSystem
from noc.core.translation import ugettext as _


class TTSystemApplication(ExtDocApplication):
    """
    TTSystem application
    """
    title = _("TT System")
    menu = [_("Setup"), _("TT System")]
    model = TTSystem
