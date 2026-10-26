# ---------------------------------------------------------------------
# peer.peergroup application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.peer.models.peergroup import PeerGroup
from noc.services.web.base.extmodelapplication import ExtModelApplication


class PeerGroupApplication(ExtModelApplication):
    """
    PeerGroup application
    """

    title = _("Peer Groups")
    menu = [_("Setup"), _("Peer Groups")]
    model = PeerGroup
    query_fields = ["name__icontains", "description__icontains"]
