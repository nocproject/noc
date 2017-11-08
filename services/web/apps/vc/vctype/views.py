# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# vc.vctype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.vc.models import VCType


class VCTypeApplication(ExtModelApplication):
    """
    VCType application
    """
    title = _("VC Type")
    menu = [_("Setup"), _("VC Types")]
    model = VCType
    query_fields = ["name"]
    query_condition = "icontains"
