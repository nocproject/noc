# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zebra
## OS:     Zebra
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Zebra.Zebra"
    supported_schemes = [TELNET, SSH]
    pattern_more = "^--More-- "
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^\S+?#"
    command_more = " "
    command_disable_pager = "terminal length 0"
    requires_netmask_conversion = True

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
