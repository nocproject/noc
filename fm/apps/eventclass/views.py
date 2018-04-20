# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.eventclass application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models.eventclass import EventClass, EventClassCategory


class EventClassApplication(ExtDocApplication):
    """
    EventClass application
    """
    title = "Event Class"
    menu = "Setup | Event Classes"
    model = EventClass
    parent_model = EventClassCategory
    parent_field = "parent"
    query_fields = ["name", "description"]
    query_condition = "icontains"
