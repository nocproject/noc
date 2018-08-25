# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sla.slaprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.sla.models.slaprofile import SLAProfile
from noc.core.translation import ugettext as _


class SLAProfileApplication(ExtDocApplication):
    """
    SLAProfile application
    """
    title = "SLA Profile"
    menu = [_("Setup"), _("SLA Profiles")]
    model = SLAProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
