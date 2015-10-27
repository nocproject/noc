# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Fortinet
## OS:     FortiOS v4.X
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Fortinet.Fortigate"
    pattern_more = "^--More--"
    pattern_prompt = r"^\S+\ #"
    command_more = " "
