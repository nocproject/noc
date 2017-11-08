# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# gis.area application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.gis.models import Area
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class AreaApplication(ExtDocApplication):
    """
    Area application
    """
    title = _("Area")
    menu = [_("Setup"), _("Areas")]
    model = Area
