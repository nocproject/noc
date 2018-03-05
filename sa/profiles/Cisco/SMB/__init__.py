# -*- coding: utf-8 -*-
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
    pattern_more = [
        (r"^More:", " "),
        (r"^Overwrite file \[startup-config\]", "y")
    ]
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = \
        r"% Invalid input detected at|% Ambiguous command:|" \
        r"% Incomplete command.|% Unrecognized command"
    pattern_operation_error = r"^%\s*bad"
    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config"
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

    def setup_session(self, script):
        script.cli("terminal no prompt")

    def shutdown_session(self, script):
        script.cli("terminal no datadump")
        script.cli("terminal prompt")


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
