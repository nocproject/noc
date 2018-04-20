# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Ubiquiti
# OS:     AirOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ubiquiti.AirOS"
    pattern_username = "([Uu][Bb][Nn][Tt] login|[Ll]ogin):"
=======
##----------------------------------------------------------------------
## Vendor: Ubiquiti
## OS:     AirOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Ubiquiti.AirOS"
    supported_schemes = [TELNET, SSH]
    pattern_username = "([Uu][Bb][Nn][Tt] login|[Ll]ogin):"
    pattern_password = "[Pp]assword:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_more = "CTRL\+C.+?a All"
    pattern_prompt = r"^\S+?\.v(?P<version>\S+)#"
    command_more = "a"
    config_volatile = ["^%.*?$"]
