# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     CatOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.CatOS"
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^\S+?\s+\(enable\)\s+"
    convert_mac = BaseProfile.convert_mac_to_dashed
    pattern_more = [
                    ("^--More--$", " "),
                    ("^Do you wish to continue y/n [n]?", "y\n")
                    ]
    config_volatile = ["^This command shows non-default configurations only.*?^Use 'show config all' to show both default and non-default configurations.", r"^\.+\s*$", r"^(?:(?:begin)|(?:end))\s*$"]
    rogue_chars = ["\r", " \x08", "\x08"]
