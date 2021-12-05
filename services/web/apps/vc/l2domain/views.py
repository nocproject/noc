# ----------------------------------------------------------------------
# vc.l2domain application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.vc.models.l2domain import L2Domain
from noc.lib.app.decorators.state import state_handler
from noc.core.translation import ugettext as _


@state_handler
class L2DomainApplication(ExtDocApplication):
    """
    L2 Domain application
    """

    title = "L2 Domain"
    menu = [_("L2 Domain")]
    model = L2Domain
    query_fields = ["name", "description"]
    query_condition = "icontains"
    int_query_fields = ["vlan"]

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    def clean_list_data(self, data):
        return data
