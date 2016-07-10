# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.community application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import Community

class CommunityApplication(ExtModelApplication):
    """
    Community application
    """
    title = "Communities"
    menu = "Communities"
    model = Community
    query_fields = ["community__icontains", "description__icontains"]
