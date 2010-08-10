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
    class Vars:
        ifindex=Var(required=True,repeat=False)
        status=Var(required=True,repeat=False)
##
## Autonegotiation Failed
##
class AutonegatiationFailed(EventClass):
    name     = "Autonegotiation Failed"
    category = "NETWORK"
    priority = "WARNING"
    subject_template="Autonegotiation has been failed at port {{interface}}"
    body_template="""Link speed and duplex mode negotiation had beed failed at port {{interface}}"""
    repeat_suppression=True
    repeat_suppression_interval=600
    class Vars:
        interface=Var(required=True,repeat=False)
