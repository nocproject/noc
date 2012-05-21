# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.eventtrigger application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.fm.models import EventTrigger


class EventTriggerApplication(ExtModelApplication):
    """
    EventTrigger application
    """
    title = "Event Triggers"
    menu = "Setup | Event Triggers"
    model = EventTrigger
