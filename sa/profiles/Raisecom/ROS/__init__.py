# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Raisecom
## OS:     ROS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Raisecom.ROS"
    pattern_more = "^ --More--"
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^\S+?#"
    command_more = " "
    command_exit = "exit"

    rx_ver = re.compile(
        r"Product name: (?P<platform>\S+)\s*\n"
        r"ROS\s+Version\s*(?P<version>\S+)\.\s*\(Compiled.+\)\s*\n"
        r"Support ipv6\s*:\s*\S+\s*\n"
        r"Bootstrap\s*Version\s*(?P<bootstrap>\S+)\s*\n"
        r"FPGA Version\s*\n"
        r"Hardware\s*\S+\s*Version Rev\.\s*(?P<hw_rev>\S+)\s*\n\n"
        r"System MacAddress is\s*:\s*(?P<mac>\S+)\s*\n"
        r"Serial number\s*:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE)

    def get_version(self, script):
        c = script.cli("show version", cached=True)
        return self.rx_ver.search(c).groupdict()

    def get_interface_names(self, name):
        r = []
        if name.startswith("port "):
            r += [name[5:]]
        else:
            r += ["port %s" % name]
        return r
