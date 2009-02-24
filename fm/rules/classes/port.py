# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Port events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## Port Trunk Status Change
##
class PortTrunkStatusChange(EventClass):
    name     = "Port Trunk Status Change"
    category = "NETWORK"
    priority = "WARNING"
    subject_template="Port {{ifindex}} changed trunk status to {{status}}"
    body_template="""Port {{ifindex}} changed trunk status to {{status}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        ifindex=Var(required=True,repeat=False)
        status=Var(required=True,repeat=False)
