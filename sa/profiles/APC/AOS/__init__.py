# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: APC
## OS:     AOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "APC.AOS"
    pattern_username = r"^User Name\s+:"
    pattern_password = r"^Password\s+:"
    pattern_prompt = r"^(\S+)?>"
    pattern_more = r"^Press <ENTER> to continue...$"
    command_submit = "\r"
