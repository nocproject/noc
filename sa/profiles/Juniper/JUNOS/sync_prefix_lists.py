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

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.sync_prefix_lists"
    implements=[ISyncPrefixLists]
    def execute(self,changed_prefix_lists):
        result=[]
        with self.configure():
            for l in changed_prefix_lists:
                name=l["name"]
                # Generate prefix list
                pl=self.profile.generate_prefix_list(name,l["prefix_list"],l["strict"])
                # Install new prefix list
                self.cli("top")
                self.cli("delete policy-options policy-statement %s"%name)
                self.cli("edit policy-options policy-statement %s"%name)
                self.cli("load merge relative terminal")
                r=self.cli(pl+"\x04",bulk_lines=25)
                result+=[{"name":name,"status":"load complete" in r}]
        return result
