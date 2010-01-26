# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.sync_prefix_lists
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import ISyncPrefixLists
import re,difflib

rx_pl=re.compile(r"^set policy-options policy-statement \S+ term pass from route-filter (\S+) (\S+)$")

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.sync_prefix_lists"
    implements=[ISyncPrefixLists]
    TIMEOUT=1800
    def execute(self,changed_prefix_lists):
        actions=[]
        result=[]
        for l in changed_prefix_lists:
            name=l["name"]
            suffix="exact" if l["strict"] else "orlonger"
            # Retrieve prefix list
            pl=self.cli("show configuration policy-options policy-statement %s | display set | no-more"%name)
            applied_pl=[]
            for ln in pl.splitlines():
                match=rx_pl.match(ln)
                if match:
                    applied_pl+=["%s %s"%(match.group(1),match.group(2))]
            # Compare prefix-lists and make the changeset
            new_pl=["%s %s"%(x,suffix) for x in l["prefix_list"]]
            for d in difflib.ndiff(sorted(applied_pl),sorted(new_pl)):
                code=d[:2]
                rest=d[2:]
                if code=="- ": # To delete
                    actions+=["delete policy-options policy-statement %s term pass from route-filter %s"%(name,rest)]
                elif code=="+ ": # To create
                    actions+=["set policy-options policy-statement %s term pass from route-filter %s"%(name,rest)]
            #
            result+=[{"name":name,"status":True}]
        # Apply changeset
        if actions:
            with self.configure():
                for cmd in actions:
                    self.cli(cmd)
        return result
