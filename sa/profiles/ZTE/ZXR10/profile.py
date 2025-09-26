# ---------------------------------------------------------------------
# Vendor: ZTE
# OS:     ZXR10
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXR10"

    pattern_more = [
        (rb"^ --More--", b" "),
        (rb"^----- more ----- Press Q or Ctrl\+C to break -----", b" "),
    ]
    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_syntax_error = (
        rb"%\s+Invalid input detected at|%\s+Parameter too much|%\s+Command not found"
    )
    command_disable_pager = "terminal length 0"
    command_super = b"enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write\n"
    pattern_prompt = rb"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco
    config_volatile = [r"^ntp clock-period .*?^"]
    telnet_naws = b"\x7f\x7f\x7f\x7f"

    def get_interface_type(cls, name):
        ifnum: str = name.split()[0]
        if ifnum.isdigit():
            # SNMP: port 25
            return "physical"
        if name.startswith("gei"):
            return "physical"
        if name.startswith("xgei"):
            return "physical"
        if name.startswith("smartgroup"):
            return "aggregated"
        if name.startswith("lo"):
            return "loopback"
        if name.startswith("vlan"):
            return "SVI"
        if name.startswith("null"):
            return "null"
        raise Exception("Cannot detect interface type for %s" % name)

        return "other"

    def convert_interface_name(self, s):
        if s.count(" "):
            return s.split(" ")[0]
        if s.startswith("port-"):
            return s.split("-", 1)[-1]
        return s
