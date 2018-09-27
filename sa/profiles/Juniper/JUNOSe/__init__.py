# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Juniper
# OS:     JUNOSe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    """
    Juniper.JUNOSe profile
    """
    name = "Juniper.JUNOSe"
    pattern_unprivileged_prompt = r"^\S+?>"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    pattern_prompt = r"^(?P<prompt>\S+?)(?::\S+?)?#"
    pattern_more = r"^ --More-- "
    command_more = " "
    command_exit = "exit"
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

    rx_adapter = re.compile(
        r"^(?P<slot>\d+/\d+)\s+(?P<name>\S+(?: \S+)+?)\s+"
        r"\d{10}\s+\d{10}\s+\S{3}\s+\d+\s*$")

    def get_interfaces_list(self, script):
        r = []
        v = script.cli("show hardware")
        for l in v.split("\n"):
            match = self.rx_adapter.search(l)
            if match:
                if match.group("name") == "10GE PR IOA":
                    r += ["TenGigabitEthernet%s/0" % match.group("slot")]
                elif match.group("name") == "GE-4 IOA":
                    for i in range(0, 4):
                        r += ["GigabitEthernet%s/%s" % (match.group("slot"), i)]
                elif match.group("name") == "SRP IOA":
                    r += ["FastEthernet%s/0" % match.group("slot")]
        return r

    def valid_interface_name(self, name):
        if "." in name:
            try:
                ifname, unit = name.split(".")
            except ValueError:
                return True
            # See `logical-interface-unit-range`
            if int(unit) > 16385:
                return False
        return True
