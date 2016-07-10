# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.ttsystem application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models.ttsystem import TTSystem


class TTSystemApplication(ExtDocApplication):
    """
    TTSystem application
    """
    title = "TT System"
    menu = "Setup | TT System"
    model = TTSystem
