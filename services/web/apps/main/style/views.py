# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.style application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.main.models.style import Style
from noc.sa.interfaces.base import ColorParameter


class StyleApplication(ExtModelApplication):
    """
    Style application
    """
    title = _("Style")
    menu = [_("Setup"), _("Styles")]
    model = Style
    icon = "icon_style"

    clean_fields = {
        "background_color": ColorParameter(),
        "font_color": ColorParameter()
    }

    def field_row_class(self, o):
        return o.css_class_name

    def field_font_color(self, o):
        if o is None:
            return None
        else:
            return "%06X" % o.font_color

    def field_background_color(self, o):
        if o is None:
            return None
        else:
            return "%06X" % o.background_color

    @view(url=r"^css/$", method=["GET"], access=True)
    def view_css(self, request):
        text = "\n\n".join([s.css for s in Style.objects.all()])
        return self.render_plain_text(text, mimetype="text/css")
