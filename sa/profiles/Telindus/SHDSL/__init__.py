# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Telindus
## OS:     SHDSL
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.core.profile.base import BaseProfile

class Profile(BaseProfile):
    name = "Telindus.SHDSL"
    username_submit = "\r"
    password_submit = "\r"
    command_exit = "DISCONNECT"