# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Huawei
## OS:     VRP3
## Compatible: 3.1
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH
import re


class Profile(noc.sa.profiles.Profile):
    name = "Huawei.VRP3"
    supported_schemes = [TELNET, SSH]
    pattern_username = r"^> User name \(<\d+ chars\): "
    pattern_password = r"^> Password \(<\d+ chars\): "
    pattern_more = [
        (r"^--More\(Enter: next line, spacebar: next page, any other key: quit\)--", " "),
        (r"\[<frameId/slotId>\]", "\n"),
        (r"\(y/n\) \[n\]", "y\n")
    ]
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "save\ny\n"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config\S*[^\)]*\))?#"
