# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS specific EIGRP rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.eigrp import *
##
## Cisco.IOS EIGRP Neighbor Up SYSLOG
##
class Cisco_IOS_EIGRP_Neighbor_Up_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS EIGRP Neighbor Up SYSLOG"
    event_class=EIGRPNeighborUp
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%DUAL-5-NBRCHANGE: IP-EIGRP\(\d+\) \d+: Neighbor (?P<ip>\S+) \((?P<interface>\S+)\) is up"),
    ]
##
## Cisco.IOS EIGRP Neighbor Down SYSLOG
##
class Cisco_IOS_EIGRP_Neighbor_Down_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS EIGRP Neighbor Down SYSLOG"
    event_class=EIGRPNeighborDown
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%DUAL-5-NBRCHANGE: IP-EIGRP\(\d+\) \d+: Neighbor (?P<ip>\S+) \((?P<interface>\S+)\) is down"),
    ]
