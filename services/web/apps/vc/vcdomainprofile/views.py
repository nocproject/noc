# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.vcdomainprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.vc.models.vcdomainprofile import VCDomainProfile
from noc.core.translation import ugettext as _


class VCDomainProfileApplication(ExtDocApplication):
    """
    VCDomainProfile application
    """
    title = "VC Domain Profile"
    menu = [_("Setup"), _("VC Domain Profile")]
    model = VCDomainProfile
