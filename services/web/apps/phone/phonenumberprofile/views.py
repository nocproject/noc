# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# phone.phonenumberprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.phone.models.phonenumberprofile import PhoneNumberProfile
from noc.core.translation import ugettext as _


class PhoneNumberProfileApplication(ExtDocApplication):
    """
    PhoneNumberProfile application
    """
    title = "Number Profile"
    menu = [_("Setup"), _("Number Profiles")]
    model = PhoneNumberProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
