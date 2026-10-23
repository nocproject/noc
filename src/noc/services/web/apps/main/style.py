# ---------------------------------------------------------------------
# main.style application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, api
from noc.main.models.style import Style
from noc.sa.interfaces.base import ColorParameter
from noc.core.translation import ugettext as _


class StyleApplication(ExtModelApplication):
    """
    Style application
    """

    title = _("Style")
    menu = [_("Setup"), _("Styles")]
    model = Style
    icon = "icon_style"

    clean_fields = {"background_color": ColorParameter(), "font_color": ColorParameter()}

    @api.get("^scheme/$", access=True)
    def api_style(self, request: HttpRequest):
        return Style.get_scheme()
