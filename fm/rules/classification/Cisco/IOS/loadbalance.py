# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco loadbalancer's events
## Modules: CSM
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.loadbalance import *
##
## Cisco.IOS CSM LB Pool Member Down SYSLOG
##
class Cisco_IOS_CSM_LB_Pool_Member_Down_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS CSM LB Pool Member Down SYSLOG"
    event_class=LBPoolMemberDown
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%CSM_SLB-6-RSERVERSTATE: Module \d+ server state changed: .* health probe failed for server (?P<node>[^:]+):(?P<port>\d+) in"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS CSM LB Pool Member Up SYSLOG
##
class Cisco_IOS_CSM_LB_Pool_Member_Up_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS CSM LB Pool Member Up SYSLOG"
    event_class=LBPoolMemberUp
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%CSM_SLB-6-RSERVERSTATE: Module \d+ server state changed: .* health probe re-activated server (?P<node>[^:]+):(?P<port>\d+) in"),
        (r"^source$",r"^syslog$"),
    ]
