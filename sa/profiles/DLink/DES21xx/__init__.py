# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: D-Link
# OS:     DES21xx
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DES21xx"
=======
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DES21xx
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET


class Profile(noc.sa.profiles.Profile):
    name = "DLink.DES21xx"
    supported_schemes = [TELNET]
    pattern_password = "[Pp]assword:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_prompt = r"^\S+?>"
    command_exit = "logout"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    telnet_slow_send_password = True
    command_submit = "\r"
