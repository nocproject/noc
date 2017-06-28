# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.pool application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.main.models.pool import Pool
from noc.core.translation import ugettext as _


class PoolApplication(ExtDocApplication):
    """
    Pool application
    """
    title = _("Pool")
    menu = [_("Setup"), _("Pools")]
    model = Pool
    glyph = "database"
