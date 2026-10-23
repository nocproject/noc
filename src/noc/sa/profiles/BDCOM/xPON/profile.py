# ---------------------------------------------------------------------
# Vendor: BDCOM
# OS:     xPON
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "BDCOM.xPON"

    pattern_more = [(rb"^ --More-- ", b" "), (rb"\(y/n\) \[n\]", b"y\n")]
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>"
    pattern_prompt = rb"^(?P<hostname>\S+)(?:_config(?:_\S+)?)?#"
    pattern_syntax_error = rb"% Unknown command"
    command_disable_pager = ["terminal length 0", "terminal width 0"]
    command_super = b"enable"
    command_enter_config = "config"
    command_leave_config = "exit"
    command_save_config = "write"
    command_exit = "exit"
    config_volatile = ["^%.*?$"]

    matchers = {
        "is_gpon": {"platform": {"$regex": r"^GP"}},
    }

    def convert_interface_name(self, interface):
        if interface.startswith("TGigaEthernet") or interface.startswith("GigaEthernet"):
            return interface
        if ":" in interface:
            interface = interface.split(":")[0]
        if interface.lower().startswith("gpon"):
            return "GPON" + interface[4:]
        if interface.lower().startswith("epon"):
            return "EPON" + interface[4:]
        if interface.startswith("f"):
            return interface.replace("f", "FastEthernet")
        if interface.startswith("g"):
            return interface.replace("g", "GigaEthernet")
        if interface.startswith("Gig"):
            return interface.replace("Gig", "GigaEthernet")
        if interface.startswith("TGi"):
            return interface.replace("TGi", "TGigaEthernet")
        if interface.startswith("tg"):
            return interface.replace("tg", "TGigaEthernet")
        if interface.startswith("v"):
            return interface.replace("v", "VLAN")
        if interface.startswith("n"):
            return interface.replace("n", "Null")
        return interface
