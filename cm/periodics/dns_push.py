# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic

class Task(noc.sa.periodic.Task):
    name="cm.dns_push"
    description=""
    wait_for=["cm.dns_pull"]
    def execute(self):
        from noc.cm.models import DNS
        DNS.global_push()
        return True

