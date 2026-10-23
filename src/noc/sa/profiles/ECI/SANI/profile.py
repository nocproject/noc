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

    pattern_username = rb"^login : "
    pattern_password = rb"^password : "
    pattern_prompt = rb"^( >>|\S+ >(?: \S+ >)?)"
    pattern_more = [(rb"press <SPACE> to continue or <ENTER> to quit", b"               \n")]
    command_exit = "logout"
