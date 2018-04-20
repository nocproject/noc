# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Zyxel
# OS:     ZyNOS_EE
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.ZyNOS_EE"
=======
##----------------------------------------------------------------------
## Vendor: Zyxel
## OS:     ZyNOS_EE
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Zyxel.ZyNOS_EE"
    supported_schemes = [TELNET, SSH]
#    pattern_username="User name:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_password = "Password: "
    pattern_prompt = r"^\S+?> "
    pattern_more = r"^-- more --.*?$"
    command_more = " "
    command_exit = "exit"
<<<<<<< HEAD
    enable_cli_session = False
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_save_config = "config save"
    pattern_syntax_error = r"^Valid commands are:"
