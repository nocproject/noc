# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.ignorepattern application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import IgnorePattern


class IgnorePatternApplication(ExtDocApplication):
    """
    IgnorePattern application
    """
    title = "Ignore Patterns"
    menu = "Setup | Ignore Patterns"
    model = IgnorePattern
