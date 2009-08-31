# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Huawei
## OS:     VRP
## Compatible: 3.1
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Huawei.VRP"
    supported_schemes=[TELNET,SSH]
    pattern_more="^  ---- More ----"
    pattern_prompt=r"^[<#]\S+?[>#]"
    command_more=" "
    config_volatile=["^%.*?$"]

    def generate_prefix_list(self,name,pl,strict=True):
        p="ip ip-prefix %s permit %%s"%name
        if not strict:
            p+=" le 32"
        return "undo ip ip-prefix %s\n"%name+"\n".join([p%x.replace("/"," ") for x in pl])
