# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT9900
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT9900"
=======
##----------------------------------------------------------------------
## Vendor: Allied Telesis
## OS:     AT9900
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "AlliedTelesis.AT9900"
    supported_schemes = [TELNET, SSH]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_username = r"^.*\slogin: "
    pattern_more = r"^--More--.*"
    command_more = "c"
    command_submit = "\r"
    command_save_config = "create config=boot1.cfg"
    pattern_prompt = r"^Manager.*>"
<<<<<<< HEAD
    convert_mac = BaseProfile.convert_mac_to_cisco
=======
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_cisco
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
