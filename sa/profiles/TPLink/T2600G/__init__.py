# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: TPLink
# OS:     T2600G
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
## Python modules
#import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "TPLink.T2600G"
    pattern_username = r"^User:"
    pattern_more = r"Press any key to continue \(Q to quit\)"
    pattern_unprivileged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9/.]\S{0,35})(?:[-_\d\w]+)?" \
        r"(?:\(config[^\)]*\))?#"
    command_disable_pager = "terminal length 0"
    username_submit = "\r\n"
    password_submit = "\r\n"
    command_submit = "\r\n"
    command_more = " "
    command_enter_config = "configure"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config\n"
    requires_netmask_conversion = True

    matchers = {
        "is_platform_T2600G": {
            "platform": {
                "$regex": r"T2600G.*"
            }
        }
    }

    def setup_session(self, script):
        script.cli("terminal no prompt")

    def shutdown_session(self, script):
        script.cli("terminal no datadump")
        script.cli("terminal prompt")
