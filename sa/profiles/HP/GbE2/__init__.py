# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: HP
# OS:     GbE2c
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.GbE2"
=======
##----------------------------------------------------------------------
## Vendor: HP
## OS:     GbE2c
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "HP.GbE2"
    supported_schemes = [TELNET, SSH]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_more = "Press q to quit, any other key to continue"
    pattern_prompt = r"^>> [^#]+# "
    command_more = " "
    command_leave_config = "apply"
    command_save_config = "save\ny\n"
    config_volatile = [r"^/\* Configuration dump taken.*?$"]
    rogue_chars = ["\x08"]
