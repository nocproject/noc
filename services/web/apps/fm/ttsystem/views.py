# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.ttsystem application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.fm.models.ttsystem import TTSystem
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class TTSystemApplication(ExtDocApplication):
    """
    TTSystem application
    """
    title = _("TT System")
    menu = [_("Setup"), _("TT System")]
    model = TTSystem
