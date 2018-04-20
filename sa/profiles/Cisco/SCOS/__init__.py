# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     SCOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.SCOS"
=======
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     SCOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Cisco.SCOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_more = [
        (r"--More--", " "),
        (r"\?\s*\[confirm\]", "\n")
    ]
<<<<<<< HEAD
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = \
        r"% invalid input |% Ambiguous command:|% Incomplete command."
=======
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% invalid input |% Ambiguous command:|% Incomplete command."
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
#    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config\n"
<<<<<<< HEAD
    pattern_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9]\S*?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco
=======
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9]\S*?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = NOCProfile.convert_mac_to_cisco
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def convert_interface_name(self, interface):
        if interface.startswith("Fast"):
            return "Fa " + interface[12:].strip()
<<<<<<< HEAD
        elif interface.startswith("Giga"):
=======
        elif interface.startswith("Giga"): 
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            return "Gi " + interface[15:].strip()
        elif interface.startswith("Ten"):
            return "Te " + interface[18:].strip()
        else:
            return interface
