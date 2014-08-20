# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DxS
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET


class Profile(noc.sa.profiles.Profile):
    name = "DLink.DxS_Smart"
    supported_schemes = [TELNET]
    pattern_username = "([Uu]ser ?[Nn]ame|[Ll]ogin):"
    pattern_password = "[Pp]ass[Ww]ord:"
    pattern_more = [
        ("--More--", " "),
        ("CTRL\+C.+?(a All)|(r Refresh)", "a")
    ]
    pattern_unpriveleged_prompt = r"^\S+:(3|6|user|operator)#"
    pattern_syntax_error = r"(% Invalid (Command|input detected at))|"
    r"((Available commands|Next possible completions):)"
    command_super = "enable admin"
    pattern_prompt = r"(?P<hostname>\S+(:\S+)*)[#>]"
    command_disable_pager = ""
    command_more = " "
    command_exit = "logout"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    #
    # Version comparison
    # Version format:
    # <major>.<minor><sep><patch>
    #
    rx_ver = re.compile(r"\d+")

    def cmp_version(self, x, y):
        return cmp(
            [int(z) for z in self.rx_ver.findall(x)],
            [int(z) for z in self.rx_ver.findall(y)])

    def get_pmib(self, v):
        if DGS121052(v):
            return "1.3.6.1.4.1.171.10.76.17"
        if DGS121048(v):
            return "1.3.6.1.4.1.171.10.76.11"
        if DES1210(v):
            return "1.3.6.1.4.1.171.10.75.7"
        return None


# DES-1210-series
def DES1210(v):
    return v["platform"].startswith("DES-1210")


# DGS-1210-series
def DGS121048(v):
    return v["platform"].startswith("DGS-1210-48")


def DGS121052(v):
    return v["platform"].startswith("DGS-1210-52")
