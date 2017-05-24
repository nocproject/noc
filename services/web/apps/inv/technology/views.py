# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.technology application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.technology import Technology
from noc.core.translation import ugettext as _


class TechnologyApplication(ExtDocApplication):
    """
    Technology application
    """
    title = _("Technology")
    menu = [_("Setup"), _("Technologies")]
    model = Technology
    search = ["name"]
