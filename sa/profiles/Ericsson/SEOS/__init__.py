# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Ericsson
# OS:     SEOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    """
    For correct polling on snmp it is necessary to enable "snmp extended read" in settings
    """
    name = "Ericsson.SEOS"
    pattern_more = "^---(more)---"
    pattern_unprivileged_prompt = \
        r"^(?:\[(?P<context>\S+)\])?(?P<hostname>\S+)>"
    pattern_prompt = r"^(?:\[(?P<context>\S+)\])?(?P<hostname>\S+)#"
    pattern_syntax_error = r"% Invalid input at|% ERROR Invalid input detected"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    rogue_chars = [re.compile(r"\x08{4,}\S+"), "\r"]
