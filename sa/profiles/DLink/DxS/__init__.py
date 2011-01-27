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
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="DLink.DxS"
    supported_schemes=[TELNET,SSH]
    pattern_username="([Uu]ser ?[Nn]ame|[Ll]ogin):"
    pattern_password="[Pp]ass[Ww]ord:"
    pattern_more="CTRL\+C.+?a All"
    pattern_unpriveleged_prompt=r"^\S+:(3|6|user|operator)#"
    pattern_syntax_error=r"(Available commands|Next possible completions):"
    command_super="enable admin"
    pattern_prompt=r"^(?P<hostname>\S+(:\S+)*)#"
    command_disable_pager="disable clipaging"
    command_more="a"
    command_exit="logout"
    command_save_config="save"
    config_volatile=["^%.*?$"]
    ##
    ## Version comparison
    ## Version format:
    ## <major>.<minor><sep><patch>
    ##
    rx_ver=re.compile(r"\d+")
    def cmp_version(self, x, y):
        return cmp([int(z) for z in self.rx_ver.findall(x)], [int(z) for z in self.rx_ver.findall(y)])

## DES-3200-series
def DES3200(v):
    return v["platform"].startswith("DES-3200")

## DGS-3100-series
def DGS3100(v):
    return v["platform"].startswith("DGS-3100")

## DGS-3400-series
def DGS3400(v):
    return v["platform"].startswith("DGS-34")

## DGS-3600-series
def DGS3600(v):
    return "DGS-3610" not in v["platform"] and v["platform"].startswith("DGS-36")
