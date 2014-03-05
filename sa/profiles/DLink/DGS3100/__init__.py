# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DGS3100
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "DLink.DGS3100"
    supported_schemes = [TELNET, SSH]
    pattern_username = "[Uu]ser[Nn]ame:"
    pattern_password = "[Pp]ass[Ww]ord:"
    pattern_more = [
                    (r"CTRL\+C.+?a ALL", "a"),
                    (r"\[Yes/press any key for no\]", "Y")
                   ]
    pattern_unpriveleged_prompt = r"^\S+:(3|6|user|operator)#"
    pattern_syntax_error = r"(Command: .+|Invalid input detected at)"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    command_more = "a"
    command_exit = "logout"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    ##
    ## Version comparison
    ## Version format:
    ## <major>.<minor><sep><patch>
    ##
    rx_ver = re.compile(r"\d+")

    def cmp_version(self, x, y):
        return cmp([int(z) for z in self.rx_ver.findall(x)], [int(z) for z in self.rx_ver.findall(y)])

    def get_interface_names(self, name):
        r = []
        if name.startswith("1:"):
            r += [name[2:]]
        return r


## DGS-3100-series
def DGS3100(v):
    return v["platform"].startswith("DGS-3100")
