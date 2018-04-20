# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Vendor: Cisco
# OS:     SMB
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.SMB"
=======
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     SMB
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Cisco.SMB"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_more = [
        (r"^More:", " "),
        (r"^Overwrite file \[startup-config\]", "y")
    ]
<<<<<<< HEAD
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = \
        r"% Invalid input detected at|% Ambiguous command:|" \
        r"% Incomplete command.|% Unrecognized command"
=======
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at|% Ambiguous command:|% Incomplete command.|% Unrecodnezed command"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_operation_error = r"^%\s*bad"
    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config"
<<<<<<< HEAD
    pattern_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[-_\d\w]+)?" \
        r"(?:\(config[^\)]*\))?#"
    pattern_username = "User Name:"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_colon
    config_volatile = None

    def convert_interface_name(self, interface):
        il = interface.lower()
        if il.startswith("oob"):
            return "oob"
        return self.convert_interface_name_cisco(interface)

=======
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[-_\d\w]+)?(?:\(config[^\)]*\))?#"
    pattern_username = "User Name:"
    requires_netmask_conversion = True
    convert_mac = NOCProfile.convert_mac_to_colon
    convert_interface_name = NOCProfile.convert_interface_name_cisco
    config_volatile = None

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def setup_session(self, script):
        script.cli("terminal no prompt")

    def shutdown_session(self, script):
        script.cli("terminal no datadump")
        script.cli("terminal prompt")

<<<<<<< HEAD

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
def SGSeries(v):
    """
    SGxxx series selector
    """
    return "SG" in v["platform"]


def SFSeries(v):
    """
    SFxxx series selector
    :param v:
    :type v: dict
    :return:
    :rtype: bool
    """
    return "SF" in v["platform"]
