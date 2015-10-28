# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     JUNOSe
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    """
    Juniper.JUNOSe profile
    """
    name = "Juniper.JUNOSe"
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    pattern_prompt = r"^(?P<prompt>\S+?)(?::\S+?)?#"
    pattern_more = r"^ --More-- "
    command_more = " "
    pattern_syntax_error = r"% Invalid input detected at"
    config_volatile = [
        r"^! Configuration script being generated on.*?^",
        r"^(Please wait\.\.\.)\n",
        r"^(\.+)\n"
    ]
    rogue_chars = ["\r", "\x00", "\x0d"]

    @classmethod
    def cmp_version(cls, v1, v2):
        """
        Common forms are:
            X.Y.Z release-A.B
            X.Y.Z patch-A.B
        :param cls:
        :param v1:
        :param v2:
        :return:
        """
        def convert(v):
            return v.replace(" patch-", ".").replace(" release-", ".")

        return BaseProfile.cmp_version(convert(v1), convert(v2))

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list.
        :param name: Prefix list name
        :param pl: List of (prefix, min len, max len)
        :return:
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
