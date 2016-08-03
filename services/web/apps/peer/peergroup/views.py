# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.peergroup application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.peer.models import PeerGroup
from noc.core.translation import ugettext as _


class PeerGroupApplication(ExtModelApplication):
    """
    PeerGroup application
    """
    title = _("Peer Groups")
    menu = [_("Setup"), _("Peer Groups")]
    model = PeerGroup
    query_fields = ["name__icontains","description__icontains"]

