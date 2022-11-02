# ---------------------------------------------------------------------
# main.style application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extmodelapplication import ExtModelApplication, view
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

    def field_row_class(self, o):
        return o.css_class_name

    @view(url=r"^css/$", method=["GET"], access=True)
    def view_css(self, request):
        text = "\n\n".join([s.css for s in Style.objects.all()])
        return self.render_plain_text(text, content_type="text/css")
