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
from noc.sa.interfaces import InterfaceTypeError


class Profile(noc.sa.profiles.Profile):
    name = "DLink.DGS3100"
    supported_schemes = [TELNET, SSH]
    pattern_username = "([Uu]ser ?[Nn]ame|[Ll]ogin):"
    pattern_password = "[Pp]ass[Ww]ord:"
    pattern_more = [
        (r"CTRL\+C.+?a All", "a"),
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
        return cmp(
            [int(z) for z in self.rx_ver.findall(x)],
            [int(z) for z in self.rx_ver.findall(y)]
        )

    rx_interface_name = re.compile(
        "^.+ Port\s+(?P<port>\d+)\s+on Unit (?P<unit>\d+)"
    )
    rx2_interface_name = re.compile("^.+ Port\s+(?P<port>\d+)\s*")

    def convert_interface_name(self, s):
        match = self.rx_interface_name.match(s)
        if match:
            return match.group("unit") + '/' + match.group("port")
        match = self.rx2_interface_name.match(s)
        if match:
            return match.group("port")
        return s

    def get_interface_names(self, name):
        r = []
        if name.startswith("1:"):
            r += [name[2:]]
        return r

    def root_interface(self, name):
        return name

# DGS-3100-series
def DGS3100(v):
    return v["platform"].startswith("DGS-3100")
