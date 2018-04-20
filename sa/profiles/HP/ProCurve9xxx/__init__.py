# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: HP
# OS:     ProCurve9xxx
# ---------------------------------------------------------------------
# Copyright (C) 2007-10 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.ProCurve9xxx"
    pattern_prompt = r"\S+?(\(\S+\))?#"
    pattern_unprivileged_prompt = r"^\S+?>"
=======
##----------------------------------------------------------------------
## Vendor: HP
## OS:     ProCurve9xxx
##----------------------------------------------------------------------
## Copyright (C) 2007-10 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "HP.ProCurve9xxx"
    supported_schemes = [TELNET, SSH]
    pattern_prompt = r"\S+?(\(\S+\))?#"
    pattern_unpriveleged_prompt = r"^\S+?>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_username = r"User"
    command_disable_pager = "terminal length 1000"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write memory\n"
    command_super = "enable"
    command_exit = "exit"
