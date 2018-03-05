# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ip.addressprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.ip.models.addressprofile import AddressProfile
from noc.core.translation import ugettext as _


class AddressProfileApplication(ExtDocApplication):
    """
    AddressProfile application
    """
    title = "Address Profile"
    menu = [_("Setup"), _("Address Profiles")]
    model = AddressProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
