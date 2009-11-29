# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.update_whois_cache periodic task
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic

class Task(noc.sa.periodic.Task):
    name="peer.update_whois_cache"
    description=""
    wait_for=["cm.prefix_list_pull"]
    def execute(self):
        from noc.peer.models import WhoisCache
        return WhoisCache.update()
