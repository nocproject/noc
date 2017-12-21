# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.vlan application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app import ExtDocApplication
from noc.vc.models.vlan import VLAN
from noc.lib.app.decorators.state import state_handler
from noc.core.translation import ugettext as _


@state_handler
class VLANApplication(ExtDocApplication):
    """
    VLAN application
    """
    title = "VLAN"
    menu = [_("VLAN")]
    model = VLAN

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    def clean_list_data(self, data):
        
        return data
