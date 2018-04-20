# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Vendor: Alcatel
# HW:     7324 RU
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.7324RU"
=======
##----------------------------------------------------------------------
## Vendor: Alcatel
## HW:     7324 RU
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, HTTP


class Profile(noc.sa.profiles.Profile):
    name = "Alcatel.7324RU"
    supported_schemes = [TELNET, HTTP]
    pattern_username = "User name:"
    pattern_password = "Password:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_prompt = "^\S+>"
    command_save_config = "config save"
    command_exit = "exit"
