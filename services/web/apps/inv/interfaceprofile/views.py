# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.interfaceprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.inv.models.interfaceprofile import InterfaceProfile
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class InterfaceProfileApplication(ExtDocApplication):
    """
    InterfaceProfile application
    """
    title = _("Interface Profile")
    menu = [_("Setup"), _("Interface Profiles")]
    model = InterfaceProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
