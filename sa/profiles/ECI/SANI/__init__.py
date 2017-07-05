# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: ECI http://www.ecitele.com/
# OS:     SANI
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ECI.SANI"
    pattern_username = r"^login : "
    pattern_password = r"^password : "
    pattern_prompt = r"^( >>|\S+ >(?: \S+ >)?)"
    pattern_more = [
        (r"press <SPACE> to continue or <ENTER> to quit", "               \n"),
    ]
    command_exit = "logout"
