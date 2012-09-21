# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.style application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import Style


class StyleApplication(ExtModelApplication):
    """
    Style application
    """
    title = "Style"
    menu = "Setup | Styles"
    model = Style
    icon = "icon_style"

    def field_row_class(self, o):
        return o.css_class_name

    @view(url=r"^css/$", method=["GET"], access=True)
    def view_css(self, request):
        text = "\n\n".join([s.css for s in Style.objects.all()])
        return self.render_plain_text(text, mimetype="text/css")
