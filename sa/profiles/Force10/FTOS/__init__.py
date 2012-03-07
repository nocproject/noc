# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Force10
## OS:     FTOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Force10.FTOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = "^ ?--More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Error: Invalid input at"
    pattern_operation_error = r"% Error: "
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "write memory"
    pattern_prompt = r"^\S+?#"
    command_submit = "\r"
    convert_interface_name = NOCProfile.convert_interface_name_cisco

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list _name_. pl is a list of (prefix, min_len, max_len)
        """
        me = "    seq %d permit %s"
        mne = "    seq %d permit %s le %d"
        r = ["no ip prefix-list %s" % name]
        r += ["ip prefix-list %s" % name]
        seq = 5
        for prefix, min_len, max_len in pl:
            if min_len == max_len:
                r += [me % (seq, prefix)]
            else:
                r += [mne % (seq, prefix, max_len)]
            seq += 5
        r += ["    exit"]
        return "\n".join(r)

    @classmethod
    def cmp_version(cls, v1, v2):
        """
        Compare versions.
        Versions are in format: N1.N2[.N3[.N4[L]]]
        """
        if "a" <= v1[-1] <= "z":
            n1 = [int(x) for x in v1[:-1].split(".")] + [v1[-1]]
        else:
            n1 = [int(x) for x in v1.split(".")]
        if "a" <= v2[-1] <= "z":
            n2 = [int(x) for x in v2[:-1].split(".")] + [v2[-1]]
        else:
            n2 = [int(x) for x in v2.split(".")]
        l1 = len(n1)
        l2 = len(n2)
        if l1 > l2:
            n2 += [None] * (l1 - l2)
        elif l1 < l2:
            n1 += [None] * (l2 - l1)
        for c1, c2 in zip(n1, n2):
            r = cmp(c1, c2)
            if r != 0:
                return r
        return 0


##
## Platform matching helpers
##
def SSeries(v):
    """S-series matching heler"""
    return v["platform"].startswith("S")


def CSeries(v):
    """C-series matching helper"""
    return v["platform"].startswith("C")


def ESeries(v):
    """E-series matching helper"""
    return v["platform"].startswith("E")
