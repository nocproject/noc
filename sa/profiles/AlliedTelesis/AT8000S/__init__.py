# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Allied Telesis
## OS:     AT8000S
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="AlliedTelesis.AT8000S"
    supported_schemes=[TELNET,SSH]
    pattern_username="User Name:"
    pattern_more="^More: <space>,  Quit: q, One line: <return>"
    command_more=" "
    pattern_unpriveleged_prompt=r"^\S+?>"
    pattern_prompt=r"^\S+?#"
    command_super="enable"
    command_enter_config="configure"
    command_leave_config="exit"
    command_save_config="copy running-config startup-config"
    config_volatile=["^(?P<day>3[01]|[0-2]{0,1}\d)-(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(?P<year>\d{4}) (?P<time>\d\d:\d\d:\d\d) %\W*"]
