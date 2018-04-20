# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT8500
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT8500"
    pattern_more = \
        "^--More-- <Space> = next page, <CR> = one line, C = continuous, " \
        "Q = quit"
=======
##----------------------------------------------------------------------
## Vendor: Allied Telesis
## OS:     AT8500
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "AlliedTelesis.AT8500"
    supported_schemes = [TELNET, SSH]
    pattern_username = "Login:"
    pattern_more = "^--More-- <Space> = next page, <CR> = one line, C = continuous, Q = quit"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_more = "c"
    command_submit = "\r"
    command_save_config = "save configuration"
    pattern_prompt = r"^\S+?#"
