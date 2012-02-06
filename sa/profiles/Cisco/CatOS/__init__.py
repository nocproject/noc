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
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Cisco.CatOS"
    supported_schemes = [TELNET, SSH]
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^\S+?\s+\(enable\)\s+"
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_dashed
    pattern_more = [
                    ("^--More--$", " "),
                    ("^Do you wish to continue y/n [n]?", "y\n")
                    ]
    config_volatile = ["^This command shows non-default configurations only.*?^Use 'show config all' to show both default and non-default configurations.", r"^\.+\s*$", r"^(?:(?:begin)|(?:end))\s*$"]
    rogue_chars = ["\r", " \x08", "\x08"]
