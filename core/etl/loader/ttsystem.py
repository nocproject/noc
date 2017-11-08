# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TTSystem loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.fm.models.ttsystem import TTSystem

## NOC modules
from base import BaseLoader


class TTMapLoader(BaseLoader):
    name = "ttsystem"
    model = TTSystem
    fields = [
        "id",
        "name",
        "handler",
        "connection",
        "description"
    ]
