# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.communitytype application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import CommunityType

class CommunityTypeApplication(ExtModelApplication):
    """
    Community Types application
    """
    title = "Community Types"
    menu = "Setup | Community Types"
    model = CommunityType
    query_fields = ["name__icontains"]
