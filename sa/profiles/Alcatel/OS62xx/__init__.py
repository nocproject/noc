# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## OS:     OS62xx
## Compatible: OS LS6224
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.OS62xx"
    pattern_username = "User Name:"
    pattern_more = "^More: .*?$"
    command_more = " "
    command_disable_pager = "terminal datadump"
