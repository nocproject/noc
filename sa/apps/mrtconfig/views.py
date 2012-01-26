# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.mrtconfig application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.sa.models import MRTConfig


class MRTConfigApplication(ExtDocApplication):
    """
    MRTConfig application
    """
    title = "MRT Config"
    menu = "Setup | MRT Config"
    model = MRTConfig
