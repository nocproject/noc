# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.sync_prefix_lists
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import ISyncPrefixLists
import re

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.sync_prefix_lists"
    implements=[ISyncPrefixLists]
    def execute(self,changed_prefix_lists):
        result=[]
        with self.configure():
            for l in self.changed_prefix_lists:
                name=l["name"]
                prefix_list=l["prefix_list"]
                strict=l["strict"]
                # Generate prefix list
                pl=self.profile.generate_prefix_list(name,prefix_list,strict)
                # Install new prefix list
                self.cli("top")
                self.cli("edit policy-options policy-statement %d"%name)
                self.cli("load replace relative terminal\n%s\n0x04") # End with Ctrl+D
                result+=[{"name":name,"status":True}]
        return result
