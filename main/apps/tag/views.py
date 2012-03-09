# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.tag application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import Tag


class TagApplication(ExtModelApplication):
    """
    Tag application
    """
    title = "Tag"
    # menu = "Setup | Tag"
    model = Tag
    query_fields = ["name"]
