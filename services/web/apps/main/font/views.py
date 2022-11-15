# ----------------------------------------------------------------------
# main.font application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.main.models.font import Font
from noc.core.translation import ugettext as _


class FontApplication(ExtDocApplication):
    """
    Font application
    """

    title = "Font"
    menu = [_("Setup"), _("Fonts")]
    model = Font
    glyph = "font"
