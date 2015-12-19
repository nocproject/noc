# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.profilecheckrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.sa.models.profilecheckrule import ProfileCheckRule


class ProfileCheckRuleApplication(ExtDocApplication):
    """
    ProfileCheckRule application
    """
    title = "Profile Check Rule"
    menu = "Setup | Profile Check Rules"
    model = ProfileCheckRule
    query_fields = ["name__icontains", "description__icontains"]
