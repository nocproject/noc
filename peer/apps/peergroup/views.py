# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.peergroup application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import PeerGroup

class PeerGroupApplication(ExtModelApplication):
    """
    PeerGroup application
    """
    title = "Peer Groups"
    menu = "Setup | Peer Groups"
    model = PeerGroup
    query_fields = ["name__icontains","description__icontains"]

