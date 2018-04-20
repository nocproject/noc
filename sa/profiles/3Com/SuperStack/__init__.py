# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Vendor: 3Com
# OS:     SuperStack
# ----------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "3Com.SuperStack"
=======
##----------------------------------------------------------------------
## Vendor: 3Com
## OS:     SuperStack
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET


class Profile(noc.sa.profiles.Profile):
    name = "3Com.SuperStack"
    supported_schemes = [TELNET]
    pattern_username = "Login:"
    pattern_password = "Password:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_prompt = r"^Select menu option.*:"
    pattern_more = [
        (r"Enter <CR> for more or 'q' to quit--:", "\r"),
    ]
    command_submit = "\r"
    telnet_send_on_connect = "\r"
<<<<<<< HEAD
    convert_mac = BaseProfile.convert_mac_to_dashed
=======
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_dashed
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
