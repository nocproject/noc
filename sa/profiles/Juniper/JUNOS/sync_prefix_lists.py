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
                prefix_list=l["prefix_list"]
                strict=l["strict"]
                # Generate prefix list
                pl=self.profile.generate_prefix_list(name,prefix_list,strict)
                # Install new prefix list
                self.cli("top")
                self.cli("delete policy-options policy-statement %s"%name)
                self.cli("edit policy-options policy-statement %s"%name)
                with self.servers.ftp() as ftp:
                    url=ftp.put_data(pl)
                    r=self.cli("load merge relative %s"%url)
                    result+=[{"name":name,"status":"load complete" in r}]
                    ftp.release_data(url)
        return result
