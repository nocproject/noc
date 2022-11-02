# ---------------------------------------------------------------------
# gis.area application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.gis.models.area import Area
from noc.core.translation import ugettext as _


class AreaApplication(ExtDocApplication):
    """
    Area application
    """

    title = _("Area")
    menu = [_("Setup"), _("Areas")]
    model = Area
