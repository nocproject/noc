# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     JUNOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.JUNOS"
    supported_schemes=[TELNET,SSH]
    pattern_prompt="^({master}\n)?\S*>"
    pattern_more=r"^---\(more.*?\)---"
    command_more=" "
    pattern_lg_as_path_list=r"(?<=AS path: )(\d+(?: \d+)*)"
    pattern_lg_best_path=r"^(\s+[+*].+?\s+Router ID: \S+)"
    
    def generate_prefix_list(self,name,pl,strict=True):
        if strict:
            p="        route-filter %s exact;"
        else:
            p="        route-filter %s orlonger;"
        out=["term pass {","    from {"]+[p%x for x in pl]+["    }","    then next policy;","}"]
        out+=["term reject {","    then reject;","}"]
        return "\n".join(out)
