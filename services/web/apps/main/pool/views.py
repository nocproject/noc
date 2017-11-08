# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.pool application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.pool import Pool


class PoolApplication(ExtDocApplication):
    """
    Pool application
    """
    title = _("Pool")
    menu = [_("Setup"), _("Pools")]
    model = Pool
    glyph = "database"
    default_ordering = ["name"]
