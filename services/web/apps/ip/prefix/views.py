# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.prefix application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.ip.models import Prefix
from noc.core.translation import ugettext as _


class PrefixApplication(ExtModelApplication):
    """
    Prefix application
    """
    title = _("Prefix")
    menu = [_("Setup"), _("Prefix")]
    model = Prefix

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""
