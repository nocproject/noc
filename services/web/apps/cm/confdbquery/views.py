# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cm.confdbquery application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.cm.models.confdbquery import ConfDBQuery
from noc.core.translation import ugettext as _


class ConfDBQueryApplication(ExtDocApplication):
    """
    ConfDBQuery application
    """

    title = "ConfDBQuery"
    menu = [_("Setup"), _("ConfDB Queries")]
    model = ConfDBQuery
