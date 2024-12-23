# ---------------------------------------------------------------------
# peer.peerprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.peer.models.peerprofile import PeerProfile
from noc.core.translation import ugettext as _


class PeerProfileApplication(ExtModelApplication):
    """
    PeerGroup application
    """

    title = _("Peer Profile")
    menu = [_("Setup"), _("Peer Profiles")]
    model = PeerProfile
    query_fields = ["name__icontains", "description__icontains"]
