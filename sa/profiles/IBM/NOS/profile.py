# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: IBM
# OS:     NOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "IBM.NOS"
    pattern_more = r"^--More--"
    pattern_prompt = r"^\S+?#"
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal-length 0"
    command_super = "enable"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config\n"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco
    config_volatile = ["^ntp message\-digest\-key .*?^", "^access user .*?^"]
