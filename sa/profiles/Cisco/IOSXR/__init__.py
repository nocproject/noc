# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     IOS XR
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile
from noc.sa.interfaces.base import InterfaceTypeError


class Profile(BaseProfile):
    name = "Cisco.IOSXR"
    pattern_more = r"^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_exit = "exit"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco
    default_parser = "noc.cm.parsers.Cisco.IOSXR.base.BaseIOSXRParser"

    rx_interface_name = re.compile(
        r"^(?P<type>[a-z\-]+)\s*(?P<number>\d+(?:/\d+)*(?:\.\d+)?(?:(?:/RS?P\d+)?/CPU\d+(?:/\d+)*)?)$",
        re.IGNORECASE)

    def convert_interface_name(self, s):
        """
        MgmtEth0/1/CPU0/0
        GigabitEthernet0/2/0/0.1000
        Te0/0/1/3
        """
        match = self.rx_interface_name.match(s)
        if not match:
            raise InterfaceTypeError("Invalid interface '%s'" % s)
        t = match.group(1)[:2]
        if t.lower() == "Bu":
            t = "BE"
        return "%s%s" % (t, match.group(2))

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list _name_. pl is a list of (prefix, min_len, max_len)
        """
        me = " %s"
        mne = " %s le %d"
        r = []
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r += [me % prefix]
            else:
                r += [mne % (prefix, max_len)]
        return "\n".join([
            "prefix-set %s" % name,
            ",\n".join(r),
            "end-set"
        ])
