# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     IOS XR
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Cisco.IOSXR"
    supported_schemes = [TELNET, SSH]
    pattern_more = r"^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = noc.sa.profiles.Profile.convert_mac_to_cisco
    convert_interface_name = noc.sa.profiles.Profile.convert_interface_name_cisco
    config_volatile = [r"^ntp clock-period .*?^"]

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
