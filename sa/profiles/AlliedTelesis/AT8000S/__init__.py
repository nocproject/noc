# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Allied Telesis
## OS:     AT8000S
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "AlliedTelesis.AT8000S"
    supported_schemes = [TELNET, SSH]
    pattern_username = "User Name:"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_prompt = r"^\S+?#"
    pattern_more = [
        (r"^More: <space>,  Quit: q, One line: <return>", " "),
        (r"^.*?\[Yes/press any key for no\]\.*", "Y"),
        ]
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    command_disable_pager = "terminal datadump"
    config_volatile = [r"^\s*(?P<day>3[01]|[0-2]{0,1}\d)-(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(?P<year>\d{4}) (?P<time>\d\d:\d\d:\d\d) %\W*"]
