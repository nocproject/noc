# ----------------------------------------------------------------------
# peer.asprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.peer.models.asprofile import ASProfile
from noc.core.translation import ugettext as _


class ASProfileApplication(ExtDocApplication):
    """
    ASProfile application
    """

    title = "AS Profile"
    menu = [_("Setup"), _("AS Profiles")]
    model = ASProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
