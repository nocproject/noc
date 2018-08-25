# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.vrfgroup application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.ip.models.vrfgroup import VRFGroup
from noc.core.translation import ugettext as _


class VRFGroupApplication(ExtModelApplication):
    """
    VRFGroup application
    """
    title = _("VRF Groups")
    menu = [_("Setup"), _("VRF Groups")]
    model = VRFGroup
    query_condition = "icontains"

    def field_vrf_count(self, obj):
        return obj.vrf_set.count()
