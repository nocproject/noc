# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.classificationrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import EventClassificationRule


class EventClassificationRuleApplication(ExtDocApplication):
    """
    EventClassificationRule application
    """
    title = "Classification Rule"
    menu = "Setup | Classification Rules"
    model = EventClassificationRule
