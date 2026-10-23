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

    pattern_more = [(rb"--More--", b" "), (rb"\?\s*\[confirm\]", b"\n")]
    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_syntax_error = rb"% invalid input |% Ambiguous command:|% Incomplete command."
    #    command_disable_pager = "terminal length 0"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9]\S*?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco

    def convert_interface_name(self, interface):
        if interface.startswith("Fast"):
            return "Fa " + interface[12:].strip()
        if interface.startswith("Giga"):
            return "Gi " + interface[15:].strip()
        if interface.startswith("Ten"):
            return "Te " + interface[18:].strip()
        return interface
