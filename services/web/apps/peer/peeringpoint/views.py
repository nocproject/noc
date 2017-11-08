# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# peer.peeringpoint application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.peer.models import PeeringPoint


class PeeringPointApplication(ExtModelApplication):
    """
    Peering Point application
    """
    title = _("Peering Points")
    menu = [_("Setup"), _("Peering Points")]
    model = PeeringPoint
    query_fields = ["hostname__icontains", "router_id__icontains"]
