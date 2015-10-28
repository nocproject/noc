# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.ignoreeventrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.fm.models import IgnoreEventRules
from noc.sa.interfaces.base import REParameter


class IgnoreEventRuleApplication(ExtModelApplication):
    """
    IgnoreEventRule application
    """
    title = "Ignore Event Rules"
    menu = "Setup | Ignore Event Rules"
    model = IgnoreEventRules

    clean_fields = {
        "left_re": REParameter(),
        "right_re": REParameter()
    }
