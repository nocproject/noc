# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sla.slaprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app import ExtDocApplication
from noc.sla.models.slaprofile import SLAProfile


class SLAProfileApplication(ExtDocApplication):
    """
    SLAProfile application
    """
    title = "SLA Profile"
    menu = [_("Setup"), _("SLA Profiles")]
    model = SLAProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
