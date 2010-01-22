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
    pattern_prompt=r"^((?:{master}(\[.+?\]\n)?)?\S*[>#])|(\[Type \^D at a new line to end input\])"
    pattern_more=r"^---\(more.*?\)---"
    command_more=" "
    command_enter_config="configure"
    command_leave_config="commit and-quit"
    pattern_lg_as_path_list=r"(?<=AS path: )(\d+(?: \d+)*)"
    pattern_lg_best_path=r"^(\s+[+*].+?\s+Router ID: \S+)"
    
    def generate_prefix_list(self,name,pl,strict=True):
        if strict:
            p="set policy-options policy-statement %s term pass from route-filter %%s exact"%name
        else:
            p="set policy-options policy-statement %s term pass from route-filter %%s orlonger"%name
        out=[p%x for x in pl]+["set policy-options policy-statement %s term reject then reject"%name]
        return "\n".join(out)
