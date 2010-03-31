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
import re

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
            if len(l["prefix_list"])==0:
                result+=[{"name":name,"status":False}]
                self.error("Refusing to apply empty policy-option %s"%name)
                continue
            suffix="exact" if l["strict"] else "orlonger"
            # Retrieve prefix list
            pl=self.cli("show configuration policy-options policy-statement %s | display set | no-more"%name)
            applied_pl=set()
            for ln in pl.splitlines():
                match=rx_pl.match(ln)
                if match:
                    applied_pl.add("%s %s"%(match.group(1),match.group(2)))
            # Build new prefix-list
            new_pl=set(["%s %s"%(x,suffix) for x in l["prefix_list"]])
            # Delete obsolete records
            actions+=["delete policy-options policy-statement %s term pass from route-filter %s"%(name,x) for x in applied_pl.difference(new_pl)]
            # Add new records
            actions+=["set policy-options policy-statement %s term pass from route-filter %s"%(name,x) for x in new_pl.difference(applied_pl)]
            #
            result+=[{"name":name,"status":True}]
        # Apply changeset
        if actions:
            with self.configure():
                for cmd in actions:
                    self.cli(cmd)
        return result
