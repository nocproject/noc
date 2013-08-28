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
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.interfaces import InterfaceTypeError


class Profile(NOCProfile):
    name = "Cisco.IOSXR"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = r"^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_exit = "exit"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = NOCProfile.convert_mac_to_cisco

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
        return "%s%s" % (match.group(1)[:2], match.group(2))

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list _name_. pl is a list of (prefix, min_len, max_len)
        """
        me = "ip prefix-list %s permit %%s" % name
        mne = "ip prefix-list %s permit %%s le %%d" % name
        r = ["no ip prefix-list %s" % name]
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r += [me % prefix]
            else:
                r += [mne % (prefix, max_len)]
        return "\n".join(r)
