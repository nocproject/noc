# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# gis.area application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.gis.models import Area
from noc.core.translation import ugettext as _


class AreaApplication(ExtDocApplication):
    """
    Area application
    """
    title = _("Area")
    menu = [_("Setup"), _("Areas")]
    model = Area
