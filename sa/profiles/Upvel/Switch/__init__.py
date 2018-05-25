# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Upvel
# OS:     Switch
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Upvel.Switch"
    pattern_username = "[Ll]ogin :"
    pattern_password = "[Pp]assword :"
    pattern_prompt = r"^(?P<hostname>\S+)# )"
    command_exit = "exit"
