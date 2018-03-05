# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: D-Link
# OS:     DGS3100
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DGS3100"
    pattern_more = [
        (r"CTRL\+C.+?a All", "a"),
        (r"CTRL\+C.+?a ALL ", "a"),
        (r"\[Yes/press any key for no\]", "Y")
    ]
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+):(3|6|user|operator)#"
    pattern_syntax_error = r"(Command: .+|Invalid input detected at)"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    rogue_chars = [re.compile("^\s{45,}"), "\r"]
    command_more = "a"
    command_exit = "logout"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    send_on_syntax_error = BaseProfile.send_backspaces
    #
    # Version comparison
    # Version format:
    # <major>.<minor><sep><patch>
    #
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

    def open_brackets(self, str):
        """
        Open brackets in expression
        "1:(1-2,5,7-9),ch(2,4-5)" -> "1:1-1:2,1:5,1:7-1:9,ch2,ch4-ch5"
        """
        rx_group = re.compile(r"(?P<prefix>[ch\d\:]+)\((?P<range>[\d\-,]+)\)")
        rx_range = re.compile(r"(?P<interface>[\d]+)(?P<comma>[-,])?")
        list_in = str
        list_out = list_in
        for match in rx_group.finditer(list_in):
            group = match.group()
            # group = prefix + "(" + range + ")"
            prefix = match.group("prefix")
            range = match.group("range")
            convert_group = ""
            for match in rx_range.finditer(range):
                interface = match.group("interface")
                comma = match.group("comma")
                convert_group += prefix + interface
                if comma is not None:
                    convert_group += comma
            list_out = list_out.replace(group, convert_group)
        return list_out


# DGS-3100-series
def DGS3100(v):
    return v["platform"].startswith("DGS-3100")
