# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Protei
## OS:     MAK, MTU, ITG
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Protei.MediaGateway"
    command_submit = "\r"
    pattern_prompt = "(^\S+\$|MAK>|MTU>|ITG>)"
