# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: DLink
## OS:     DxS_Cisco_CLI
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "DLink.DxS_Cisco_CLI"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = "^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = r"^(?P<hostname>\S+?)#"
    # Don't sure. Below this line obtained from Cisco.IOS profile
    requires_netmask_conversion = True
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_cisco
    convert_interface_name = NOCProfile.convert_interface_name_cisco
    config_volatile = ["^ntp clock-period .*?^"]

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
