# ---------------------------------------------------------------------
# peer.peeringpoint application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.peer.models.peeringpoint import PeeringPoint
from noc.services.web.base.extmodelapplication import ExtModelApplication


class PeeringPointApplication(ExtModelApplication):
    """
    Peering Point application
    """

    title = _("Peering Points")
    menu = [_("Setup"), _("Peering Points")]
    model = PeeringPoint
    query_fields = ["hostname__icontains", "router_id__icontains"]
