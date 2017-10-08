# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: UTST http://www.ecitele.com/
# OS:     ONU
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "UTST.ONU"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    command_super = "enable"
    pattern_unprivileged_prompt = r"^ONU208i#|ONU2004>"
    pattern_prompt = r"^ONU208i\(enable\)|ONU2004(?:i#|#)"

    #pattern_prompt = r"^Select menu option.*:"
    #pattern_more = [
    #    (r"Enter <CR> for more or 'q' to quit--:", "\r"),
    #    (r"press <SPACE> to continue or <ENTER> to quit", "               \n"),
    #]
    command_exit = "logout"

