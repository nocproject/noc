# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: NSN
# OS:     hiX56xx
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NSN.hiX56xx"
    pattern_more = "^ --More--"
    pattern_unprivileged_prompt = r"^\S+?>"
=======
##----------------------------------------------------------------------
## Vendor: NSN
## OS:     hiX56xx
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH
import re


class Profile(noc.sa.profiles.Profile):
    name = "NSN.hiX56xx"
    supported_schemes = [TELNET, SSH]
    pattern_more = "^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "wr mem\n"
<<<<<<< HEAD
    pattern_prompt = \
        r"^(?P<hostname>\S+?)(?:-\d+)?(?:\((config|bridge)[^\)]*\))?#"
=======
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\((config|bridge)[^\)]*\))?#"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def shutdown_session(self, script):
        script.cli("terminal no length")
